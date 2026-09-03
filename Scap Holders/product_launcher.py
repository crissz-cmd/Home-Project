import base64, contextlib, hashlib, json, os, socket, threading
from datetime import datetime, timezone
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from license_public_key import PUBLIC_KEY_B64
PRODUCT="Scap Holders"
VERSION="1.0.0"
def data_dir():
    root=os.getenv("APPDATA") or str(Path.home()); p=Path(root)/"ScapHolders"; p.mkdir(parents=True,exist_ok=True); return p
def machine_id():
    raw=f"{socket.gethostname()}|{os.getenv('PROCESSOR_IDENTIFIER','')}|{os.getenv('COMPUTERNAME','')}"; return hashlib.sha256(raw.encode()).hexdigest()[:24].upper()
def canonical(p): return json.dumps(p,sort_keys=True,separators=(",",":")).encode()
def license_path(): return data_dir()/"license.key"
def settings_path(): return data_dir()/"settings.json"
def log_path(): return data_dir()/"runtime.log"
def verify_license():
    if PUBLIC_KEY_B64=="REPLACE_AT_BUILD_TIME": return None,"This build has no signing key configured."
    try:
        data=json.loads(license_path().read_text(encoding="utf-8")); sig=base64.b64decode(data.pop("signature")); expected={"product":data["product"],"license_id":data["license_id"],"machine_id":data["machine_id"],"expires_at":data["expires_at"]}
        Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBLIC_KEY_B64)).verify(sig,canonical(expected))
        if expected["product"]!=PRODUCT: return None,"License is for a different product."
        if expected["machine_id"].upper()!=machine_id(): return None,"License is activated for another PC."
        if datetime.now(timezone.utc)>=datetime.fromisoformat(expected["expires_at"].replace("Z","+00:00")): return None,"License has expired."
        return expected,""
    except FileNotFoundError: return None,"License not activated."
    except Exception as exc: return None,f"Invalid license: {exc}"
def load_settings():
    s={"symbol":"GOLDi","risk_percent":0.3,"target_profit_usd":2.0,"max_open_positions":5,"max_daily_loss_percent":2.0,"max_spread_points":30,"dry_run":True,"mt5_terminal_path":""}
    try: s.update(json.loads(settings_path().read_text(encoding="utf-8")))
    except Exception: pass
    return s
def save_settings(s): settings_path().write_text(json.dumps(s,indent=2),encoding="utf-8")
class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title(f"{PRODUCT} {VERSION}"); self.geometry("760x610"); self.resizable(False,False); self.bot_module=None; self.bot_thread=None; self.log_offset=0; self._build(load_settings()); self.after(500,self._poll_log); self._refresh_license()
    def _build(self,s):
        root=ttk.Frame(self,padding=18); root.pack(fill="both",expand=True); ttk.Label(root,text=PRODUCT,font=("Segoe UI",20,"bold")).pack(anchor="w"); ttk.Label(root,text="Automated Gold Scalping • MetaTrader 5",font=("Segoe UI",10)).pack(anchor="w",pady=(0,12))
        box=ttk.LabelFrame(root,text="License",padding=10); box.pack(fill="x"); self.license_label=ttk.Label(box); self.license_label.pack(anchor="w"); ttk.Button(box,text="Copy Machine ID",command=self.copy_machine_id).pack(anchor="e",pady=(6,0))
        form=ttk.LabelFrame(root,text="Trading Configuration",padding=10); form.pack(fill="x",pady=10); fields=[("symbol","Symbol"),("risk_percent","Risk / trade (%)"),("target_profit_usd","Profit target (USD)"),("max_open_positions","Max open positions"),("max_daily_loss_percent","Daily loss limit (%)"),("max_spread_points","Max spread (points)"),("mt5_terminal_path","MT5 terminal path")]; self.vars={}
        for r,(k,label) in enumerate(fields): ttk.Label(form,text=label).grid(row=r,column=0,sticky="w",pady=4); self.vars[k]=tk.StringVar(value=str(s[k])); ttk.Entry(form,textvariable=self.vars[k],width=48).grid(row=r,column=1,sticky="w",padx=12,pady=4)
        self.dry=tk.BooleanVar(value=bool(s["dry_run"])); ttk.Checkbutton(form,text="DRY RUN / Demo test (recommended)",variable=self.dry).grid(row=len(fields),column=1,sticky="w",pady=6)
        actions=ttk.Frame(root); actions.pack(fill="x"); ttk.Button(actions,text="Save",command=self.save).pack(side="left"); self.start_btn=ttk.Button(actions,text="Start Bot",command=self.start); self.start_btn.pack(side="right"); ttk.Button(actions,text="Stop",command=self.stop).pack(side="right",padx=8)
        self.log=tk.Text(root,height=13,state="disabled",font=("Consolas",9)); self.log.pack(fill="both",expand=True,pady=(10,0)); self._write("Ready. MetaTrader 5 must be installed and logged into the intended account.")
    def _write(self,text):
        if not text: return
        self.log.config(state="normal"); self.log.insert("end",text+"\n"); self.log.see("end"); self.log.config(state="disabled")
    def _refresh_license(self):
        lic,err=verify_license(); self.license_label.config(text=f"ACTIVE • {lic['license_id']} • expires {lic['expires_at']}" if lic else f"INACTIVE • {err}")
    def copy_machine_id(self):
        mid=machine_id(); self.clipboard_clear(); self.clipboard_append(mid); self.update(); messagebox.showinfo(PRODUCT,f"Machine ID copied:\n\n{mid}\n\nSend this ID to the seller for activation.")
    def save(self):
        try:
            s={"symbol":self.vars["symbol"].get().strip(),"risk_percent":float(self.vars["risk_percent"].get()),"target_profit_usd":float(self.vars["target_profit_usd"].get()),"max_open_positions":int(self.vars["max_open_positions"].get()),"max_daily_loss_percent":float(self.vars["max_daily_loss_percent"].get()),"max_spread_points":float(self.vars["max_spread_points"].get()),"mt5_terminal_path":self.vars["mt5_terminal_path"].get().strip(),"dry_run":bool(self.dry.get())}
            if not s["symbol"]: raise ValueError("Symbol is required.")
            if not 0<s["risk_percent"]<=5: raise ValueError("Risk must be >0 and <=5%.")
            if s["target_profit_usd"]<=0: raise ValueError("Profit target must be >0.")
            save_settings(s); self._write("Settings saved."); return s
        except Exception as exc: messagebox.showerror(PRODUCT,str(exc)); return None
    def start(self):
        lic,err=verify_license()
        if not lic: messagebox.showerror(PRODUCT,err); return
        s=self.save()
        if not s: return
        if not s["dry_run"] and not messagebox.askyesno(PRODUCT,"LIVE mode sends real orders to MT5. Continue?"): return
        os.environ.update({"MT5_TERMINAL_PATH":s["mt5_terminal_path"],"SCAP_SYMBOLS":s["symbol"],"SCAP_RISK_PERCENT":str(s["risk_percent"]),"SCAP_TARGET_PROFIT_USD":str(s["target_profit_usd"]),"SCAP_MAX_OPEN_POSITIONS":str(s["max_open_positions"]),"SCAP_MAX_DAILY_LOSS_PERCENT":str(s["max_daily_loss_percent"]),"SCAP_MAX_SPREAD_POINTS":str(s["max_spread_points"]),"SCAP_DRY_RUN":"1" if s["dry_run"] else "0","SCAP_REQUIRE_LIVE_CONFIRMATION":"0","SCAP_PRODUCT_MODE":"1"})
        if self.bot_thread and self.bot_thread.is_alive(): return
        self.log_offset=0; log_path().write_text("",encoding="utf-8"); self.start_btn.config(state="disabled"); self._write("Starting trading engine…"); self.bot_thread=threading.Thread(target=self._run_bot,daemon=True); self.bot_thread.start()
    def _run_bot(self):
        try:
            import bot; self.bot_module=bot
            with log_path().open("a",encoding="utf-8",buffering=1) as stream:
                with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream): bot.run()
        except Exception as exc: self.after(0,lambda:self._write(f"Bot error: {exc}"))
        finally: self.after(0,lambda:self.start_btn.config(state="normal"))
    def stop(self):
        if self.bot_module: self.bot_module.request_stop(); self._write("Stop requested. Waiting for engine shutdown…")
        else: self._write("Bot is not running.")
    def _poll_log(self):
        try:
            p=log_path(); text=p.read_text(encoding="utf-8",errors="replace") if p.exists() else ""
            if len(text)>self.log_offset: self._write(text[self.log_offset:].rstrip()); self.log_offset=len(text)
        except Exception: pass
        self.after(500,self._poll_log)
if __name__=="__main__": App().mainloop()
