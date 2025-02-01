import os
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Token sayım fonksiyonu: tiktoken yüklüyse onu, yoksa regex tabanlı yedek yöntemi kullanır.
try:
    import tiktoken

    def count_tokens(text):
        """
        tiktoken kullanılarak, LLM contextine uygun "cl100k_base" encoding ile token sayısını döndürür.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
except ImportError:
    def count_tokens(text):
        """
        tiktoken bulunamazsa, regex ile token sayımı yapar.
        """
        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        return len(tokens)

class FileExplorer:
    def __init__(self, master):
        self.master = master
        self.master.title("Dosya & Klasör Görüntüleyici - LLM Context Token Sayacı")
        self.master.geometry("900x600")
        
        # Kök dizin: Bu dosyanın bulunduğu dizin; navigasyon sınırı olarak kullanılır.
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.current_path = self.base_path
        
        # Dil çevirileri
        self.translations = {
            "EN": {
                "title": "File & Folder Viewer - LLM Context Token Counter",
                "directory_content": "Directory Content",
                "up_directory": "Up Directory",
                "current_dir": "Current Directory: ",
                "select_all": "Select All",
                "clear_selection": "Clear Selection",
                "source_code": "Source Code (Markdown)",
                "save": "Save (llm.txt)",
                "total_tokens": "Total Token Count: ",
                "folder": "Folder",
                "file_read_error": "File could not be read: ",
                "folder_read_error": "Error: Folder could not be read: ",
                "root_dir_info": "Already in root directory.",
                "root_dir_error": "Cannot go outside root directory.",
                "save_success": "'llm.txt' file saved:\n",
                "save_error": "File could not be saved: ",
                "list_error": "Directory content could not be listed: "
            },
            "TR": {
                "title": "Dosya & Klasör Görüntüleyici - LLM Context Token Sayacı",
                "directory_content": "Dizin İçeriği",
                "up_directory": "Üst Dizin",
                "current_dir": "Mevcut Dizin: ",
                "select_all": "Tümünü Seç",
                "clear_selection": "Seçimi Temizle",
                "source_code": "Kaynak Kod (Markdown)",
                "save": "Kaydet (llm.txt)",
                "total_tokens": "Toplam Token Sayısı: ",
                "folder": "Klasör",
                "file_read_error": "Dosya okunamadı: ",
                "folder_read_error": "Hata: Klasör okunamadı: ",
                "root_dir_info": "Zaten kök dizindesiniz.",
                "root_dir_error": "Kök dizinin dışına çıkamazsınız.",
                "save_success": "'llm.txt' dosyası kaydedildi:\n",
                "save_error": "Dosya kaydedilemedi: ",
                "list_error": "Dizin içeriği listelenemedi: "
            },
            "RU": {
                "title": "Просмотрщик файлов и папок - Счетчик токенов LLM Context",
                "directory_content": "Содержимое каталога",
                "up_directory": "Вверх",
                "current_dir": "Текущий каталог: ",
                "select_all": "Выбрать все",
                "clear_selection": "Очистить выбор",
                "source_code": "Исходный код (Markdown)",
                "save": "Сохранить (llm.txt)",
                "total_tokens": "Общее количество токенов: ",
                "folder": "Папка",
                "file_read_error": "Не удалось прочитать файл: ",
                "folder_read_error": "Ошибка: Не удалось прочитать папку: ",
                "root_dir_info": "Уже в корневом каталоге.",
                "root_dir_error": "Нельзя выйти за пределы корневого каталога.",
                "save_success": "Файл 'llm.txt' сохранен:\n",
                "save_error": "Не удалось сохранить файл: ",
                "list_error": "Не удалось получить содержимое каталога: "
            }
        }
        
        self.setup_ui()
        self.populate_listbox()
        
        # Dil değişikliğini dinle
        self.language_var.trace_add("write", self.on_language_change)
    
    def setup_ui(self):
        # Ana bölmeleri oluşturmak için PanedWindow kullanıyoruz (sol: liste, sağ: içerik)
        self.paned = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # SOL PANEL: Dizin içeriğini listeleyen alan ve navigasyon butonları
        self.left_frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(self.left_frame, weight=1)
        
        header_frame = ttk.Frame(self.left_frame)
        header_frame.pack(fill=tk.X)
        
        self.left_label = ttk.Label(header_frame, text=self.translations["EN"]["directory_content"], font=("Arial", 12, "bold"))
        self.left_label.pack(side=tk.LEFT, anchor="w")
        
        self.up_button = ttk.Button(header_frame, text=self.translations["EN"]["up_directory"], command=self.go_up_directory)
        self.up_button.pack(side=tk.RIGHT)
        
        self.current_path_label = ttk.Label(self.left_frame, text="", font=("Arial", 10))
        self.current_path_label.pack(anchor="w", pady=(5, 5))
        
        self.list_frame = ttk.Frame(self.left_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(self.list_frame, selectmode=tk.EXTENDED, font=("Consolas", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.list_scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.list_scrollbar.set)
        
        # Liste seçimi ve çift tıklama olayları
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Double-Button-1>", self.on_item_double_click)
        
        # Ek seçim kontrol butonları
        self.left_button_frame = ttk.Frame(self.left_frame)
        self.left_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.select_all_button = ttk.Button(self.left_button_frame, text=self.translations["EN"]["select_all"], command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_selection_button = ttk.Button(self.left_button_frame, text=self.translations["EN"]["clear_selection"], command=self.clear_selection)
        self.clear_selection_button.pack(side=tk.LEFT)
        
        # SAĞ PANEL: Markdown biçiminde kaynak kod ve LLM context token sayısını gösteren alan
        self.right_frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(self.right_frame, weight=3)
        
        # Üst kısım: Sağ panelin başlık alanı için grid kullanarak yerleşim ayarlanıyor.
        top_right_frame = ttk.Frame(self.right_frame)
        top_right_frame.pack(fill=tk.X)
        
        self.right_label = ttk.Label(top_right_frame, text=self.translations["EN"]["source_code"], font=("Arial", 12, "bold"))
        self.right_label.grid(row=0, column=0, sticky="w")
        
        # Sağ üst köşede: Dil modu selectbox (default "EN", seçenekler: EN, TR, RU)
        self.language_var = tk.StringVar(value="EN")
        language_combobox = ttk.Combobox(top_right_frame, values=["EN", "TR", "RU"], state="readonly", width=5, textvariable=self.language_var)
        language_combobox.grid(row=0, column=3, sticky="e", padx=(0,5))
        
        self.save_button = ttk.Button(top_right_frame, text=self.translations["EN"]["save"], command=self.save_to_file)
        self.save_button.grid(row=0, column=2, sticky="e", padx=(5,5))
        
        top_right_frame.columnconfigure(1, weight=1)
        
        self.text = tk.Text(self.right_frame, wrap=tk.NONE, font=("Consolas", 10))
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.text_scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=self.text_scrollbar.set)
        
        # Token sayısını gösteren etiket (LLM contexti için)
        self.token_count_label = ttk.Label(self.right_frame, text=self.translations["EN"]["total_tokens"] + "0", font=("Arial", 10))
        self.token_count_label.pack(side=tk.BOTTOM, anchor="e", pady=(5, 0))
        
        # <<Modified>> sanal olayı ile Text widget içeriği değiştikçe token sayısını güncelle
        self.text.bind("<<Modified>>", self.on_text_modified)
    
    def on_language_change(self, *args):
        lang = self.language_var.get()
        self.master.title(self.translations[lang]["title"])
        self.left_label.config(text=self.translations[lang]["directory_content"])
        self.up_button.config(text=self.translations[lang]["up_directory"])
        self.select_all_button.config(text=self.translations[lang]["select_all"])
        self.clear_selection_button.config(text=self.translations[lang]["clear_selection"])
        self.right_label.config(text=self.translations[lang]["source_code"])
        self.save_button.config(text=self.translations[lang]["save"])
        self.token_count_label.config(text=self.translations[lang]["total_tokens"] + str(count_tokens(self.text.get("1.0", tk.END))))
        self.populate_listbox()  # Mevcut dizin etiketini güncellemek için
    
    def populate_listbox(self):
        """Geçerli dizindeki dosya ve klasörleri alfabetik sırayla listeler."""
        try:
            items = os.listdir(self.current_path)
            items.sort(key=lambda s: s.lower())
            self.listbox.delete(0, tk.END)
            for item in items:
                self.listbox.insert(tk.END, item)
            rel_current = os.path.relpath(self.current_path, self.base_path)
            if rel_current == ".":
                rel_current = os.path.basename(self.base_path)
            lang = self.language_var.get()
            self.current_path_label.config(text=f"{self.translations[lang]['current_dir']}{rel_current}")
            if os.path.abspath(self.current_path) == os.path.abspath(self.base_path):
                self.up_button.state(["disabled"])
            else:
                self.up_button.state(["!disabled"])
        except Exception as e:
            lang = self.language_var.get()
            messagebox.showerror("Hata", f"{self.translations[lang]['list_error']}{e}")
    
    def get_markdown_for_path(self, path):
        """
        Verilen dosya veya klasör yolunun içeriğini Markdown formatında oluşturur.
          - Dosya: Göreceli yol başlık olarak, içeriği kod bloğu içinde.
          - Klasör: Klasör adı başlık olarak, içerideki tüm dosya/klasörler (rekürsif) eklenir.
        """
        rel_path = os.path.relpath(path, self.base_path)
        base_name = os.path.basename(self.base_path)
        display_path = f"{base_name}/{rel_path.replace(os.sep, '/')}"
        lang = self.language_var.get()
        
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"{self.translations[lang]['file_read_error']}{e}"
            markdown_str = f"## {display_path}\n\n```python\n{content}\n```\n\n"
            return markdown_str
        elif os.path.isdir(path):
            markdown_str = f"## {display_path} ({self.translations[lang]['folder']})\n\n"
            try:
                items = sorted(os.listdir(path), key=lambda s: s.lower())
                for item in items:
                    full_item_path = os.path.join(path, item)
                    markdown_str += self.get_markdown_for_path(full_item_path)
            except Exception as e:
                markdown_str += f"{self.translations[lang]['folder_read_error']}{e}\n\n"
            return markdown_str
        else:
            return ""
    
    def on_select(self, event):
        """
        Listbox'ta yapılan seçimlere göre, seçilen dosya veya klasörlerin Markdown içeriğini Text widget'ına ekler.
        """
        selections = event.widget.curselection()
        self.text.delete("1.0", tk.END)
        if not selections:
            self.update_token_count()
            return
        full_markdown = ""
        for index in selections:
            item_name = self.listbox.get(index)
            full_path = os.path.join(self.current_path, item_name)
            full_markdown += self.get_markdown_for_path(full_path)
        self.text.insert(tk.END, full_markdown)
        self.update_token_count()
    
    def on_item_double_click(self, event):
        """Çift tıklanan öğe bir klasörse, o klasörün içeriğine geçiş yapar."""
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        item_name = self.listbox.get(index)
        full_path = os.path.join(self.current_path, item_name)
        if os.path.isdir(full_path):
            self.current_path = full_path
            self.populate_listbox()
            self.text.delete("1.0", tk.END)
            self.update_token_count()
    
    def go_up_directory(self):
        """Üst dizine geçiş yapar (kök dizinin dışına çıkış engellenir)."""
        lang = self.language_var.get()
        if os.path.abspath(self.current_path) == os.path.abspath(self.base_path):
            messagebox.showinfo("Bilgi", self.translations[lang]["root_dir_info"])
            return
        new_path = os.path.dirname(self.current_path)
        if os.path.commonpath([self.base_path, new_path]) != os.path.abspath(self.base_path):
            messagebox.showerror("Hata", self.translations[lang]["root_dir_error"])
            return
        self.current_path = new_path
        self.populate_listbox()
        self.text.delete("1.0", tk.END)
        self.update_token_count()
    
    def select_all(self):
        """Listbox'taki tüm öğeleri seçer."""
        self.listbox.select_set(0, tk.END)
        self.on_select(tk.Event(widget=self.listbox))
    
    def clear_selection(self):
        """Listbox'taki seçimi temizler ve Text widget'ını boşaltır."""
        self.listbox.select_clear(0, tk.END)
        self.text.delete("1.0", tk.END)
        self.update_token_count()
    
    def save_to_file(self):
        """Text widget'ındaki Markdown içeriğini 'llm.txt' adıyla kök dizine kaydeder."""
        content = self.text.get("1.0", tk.END)
        file_path = os.path.join(self.base_path, "llm.txt")
        lang = self.language_var.get()
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Başarılı", f"{self.translations[lang]['save_success']}{file_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"{self.translations[lang]['save_error']}{e}")
    
    def update_token_count(self):
        """Text widget'ındaki metni alır, token sayısını hesaplar ve token sayısı etiketini günceller."""
        content = self.text.get("1.0", tk.END)
        token_count = count_tokens(content)
        lang = self.language_var.get()
        self.token_count_label.config(text=f"{self.translations[lang]['total_tokens']}{token_count}")
    
    def on_text_modified(self, event):
        """
        <<Modified>> sanal olayı tetiklendiğinde çağrılır; metindeki değişiklik sonrası token sayısını günceller.
        Not: Olay, bazı durumlarda çift tetiklenebileceğinden, edit_modified(False) ile bayrak sıfırlanır.
        """
        self.update_token_count()
        self.text.edit_modified(False)

def main():
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    app = FileExplorer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
