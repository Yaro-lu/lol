import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def remove_special_chars(text):
    """
    使用“白名单”过滤字符。
    正则表达式 [^a-zA-Z0-9\u4e00-\u9fa5\.\-_ ] 含义：
    [^...] 表示匹配“不在”括号里的所有字符。
    a-zA-Z     : 大小写英文字母
    0-9        : 数字
    \u4e00-\u9fa5: 中文汉字
    \.         : 点
    \-         : 连字符
    _          : 下划线
               : 空格
    只要不是这些字符，全部替换为空（删除）。
    """
    return re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\.\-_ ]', '', text)

class BatchRenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("严格模式：保留中英数点杠及空格下划线")
        self.root.geometry("600x450")
        self.root.configure(padx=20, pady=20)

        self.folder_path = tk.StringVar()

        # UI 构建: 顶部选择文件夹区域
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(top_frame, text="目标文件夹:", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=10)
        tk.Button(top_frame, text="浏览...", command=self.select_folder).pack(side=tk.LEFT)

        # UI 构建: 中间执行日志区域
        log_frame = tk.Frame(root)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(log_frame, text="处理日志:", font=("Arial", 10)).pack(anchor="w")
        
        # 添加滚动条和文本框
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(log_frame, yscrollcommand=scrollbar.set, height=15)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # UI 构建: 底部按钮区域
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(bottom_frame, text="开始清理 (仅留中英数、点、连字符、空格、下划线)", command=self.start_rename, 
                  bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2).pack(fill=tk.X)

    def select_folder(self):
        """打开文件夹选择对话框"""
        path = filedialog.askdirectory(title="请选择要处理的文件夹")
        if path:
            self.folder_path.set(path)
            self.log("INFO", f"已选择文件夹: {path}")

    def log(self, level, message):
        """向界面文本框添加日志信息"""
        self.log_text.insert(tk.END, f"[{level}] {message}\n")
        self.log_text.see(tk.END) # 自动滚动到最底部

    def start_rename(self):
        """执行批量重命名逻辑"""
        folder = self.folder_path.get().strip()
        if not folder:
            messagebox.showwarning("警告", "请先选择或输入一个目标文件夹！")
            return

        if not os.path.exists(folder):
            messagebox.showerror("错误", "所选的文件夹不存在！")
            return

        confirm = messagebox.askyesno("确认", "将删除所有未授权的特殊符号！\n仅保留：中英文字母、数字、点(.)、连字符(-)、空格和下划线(_)\n是否继续？")
        if not confirm:
            return

        self.log("INFO", "=== 开始严格模式处理 ===")
        renamed_file_count = 0
        renamed_dir_count = 0
        error_count = 0

        # 使用 os.walk(topdown=False) 从底层向上遍历，确保重命名父文件夹不会导致子文件路径失效
        for root_dir, dirs, files in os.walk(folder, topdown=False):
            
            # 1. 优先重命名当前层级内的所有文件
            for filename in files:
                old_path = os.path.join(root_dir, filename)
                name, ext = os.path.splitext(filename)
                
                new_name = remove_special_chars(name)
                if not new_name.strip():
                    new_name = "未命名文件"

                new_filename = new_name + ext
                new_path = os.path.join(root_dir, new_filename)

                if new_filename != filename:
                    counter = 1
                    while os.path.exists(new_path):
                        new_filename = f"{new_name}-{counter}{ext}"
                        new_path = os.path.join(root_dir, new_filename)
                        counter += 1

                    try:
                        os.rename(old_path, new_path)
                        self.log("SUCCESS", f"文件: {filename} -> {new_filename}")
                        renamed_file_count += 1
                    except Exception as e:
                        self.log("ERROR", f"重命名文件失败: {filename} (原因: {e})")
                        error_count += 1

            # 2. 接着重命名当前层级内的子文件夹
            for dirname in dirs:
                old_path = os.path.join(root_dir, dirname)
                new_name = remove_special_chars(dirname)
                
                if not new_name.strip():
                    new_name = "未命名文件夹"

                new_path = os.path.join(root_dir, new_name)

                if new_name != dirname:
                    counter = 1
                    while os.path.exists(new_path):
                        new_name_temp = f"{new_name}-{counter}"
                        new_path = os.path.join(root_dir, new_name_temp)
                        counter += 1

                    try:
                        os.rename(old_path, new_path)
                        final_dirname = os.path.basename(new_path)
                        self.log("SUCCESS", f"文件夹: {dirname} -> {final_dirname}")
                        renamed_dir_count += 1
                    except Exception as e:
                        self.log("ERROR", f"重命名文件夹失败: {dirname} (原因: {e})")
                        error_count += 1

        self.log("INFO", f"=== 处理完成！共修改了 {renamed_file_count} 个文件，{renamed_dir_count} 个文件夹，失败 {error_count} 个 ===")
        messagebox.showinfo("完成", f"批量重命名完成！\n成功修改:\n{renamed_file_count} 个文件\n{renamed_dir_count} 个文件夹。")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenameApp(root)
    root.mainloop()