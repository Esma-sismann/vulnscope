import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
from tkinter import scrolledtext

# 🔍 XSS payload
XSS_PAYLOAD = "<script>alert('XSS')</script>"

# 🧾 Formları çek
def get_forms(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find_all("form")
    except:
        return []

# 🧠 Form detaylarını al
def get_form_details(form):
    details = {}

    action = form.attrs.get("action")
    method = form.attrs.get("method", "get").lower()

    inputs = []
    for input_tag in form.find_all("input"):
        name = input_tag.attrs.get("name")
        if name:
            inputs.append(name)

    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs

    return details

# 📩 Formu gönder
def submit_form(form_details, url, payload):
    target_url = urljoin(url, form_details["action"])

    data = {}
    for name in form_details["inputs"]:
        data[name] = payload

    try:
        if form_details["method"] == "post":
            return requests.post(target_url, data=data, timeout=10)
        else:
            return requests.get(target_url, params=data, timeout=10)
    except:
        return None

# 🚀 Scan işlemi
def scan():
    output_box.delete(1.0, tk.END)

    url = url_entry.get().strip()

    if not url:
        output_box.insert(tk.END, "Lütfen bir URL gir!\n")
        return

    output_box.insert(tk.END, f"[+] Hedef: {url}\n\n")

    forms = get_forms(url)

    if not forms:
        output_box.insert(tk.END, "Form bulunamadı veya siteye erişilemedi.\n")
        return

    output_box.insert(tk.END, f"{len(forms)} form bulundu.\n\n")

    for i, form in enumerate(forms, start=1):
        details = get_form_details(form)
        response = submit_form(details, url, XSS_PAYLOAD)

        if response and XSS_PAYLOAD in response.text:
            output_box.insert(tk.END, f"[!] XSS AÇIĞI BULUNDU → Form #{i}\n")
        else:
            output_box.insert(tk.END, f"[+] Form #{i} güvenli görünüyor\n")

    output_box.insert(tk.END, "\n[✓] Tarama tamamlandı.\n")

# 🖥️ GUI
root = tk.Tk()
root.title("WebGuard - GUI Vulnerability Scanner")
root.geometry("650x450")

tk.Label(root, text="Hedef URL (http/https):").pack()

url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

tk.Button(root, text="SCAN", command=scan, bg="green", fg="white").pack(pady=10)

output_box = scrolledtext.ScrolledText(root, width=75, height=20)
output_box.pack()

root.mainloop()