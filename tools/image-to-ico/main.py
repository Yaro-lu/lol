from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image
import os

def convert_to_ico():
    input_path = entry_input.get()
    output_dir = entry_output.get()
    
    if not input_path or not output_dir:
        messagebox.showerror("错误", "请先选择图片和保存位置")
        return

    try:
        img = Image.open(input_path)
        # 创建包含多种尺寸的ICO
        sizes = [(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]
        img.save(os.path.join(output_dir, 'output.ico'), format='ICO', sizes=sizes)
        messagebox.showinfo("成功", "转换完成！")
    except Exception as e:
        messagebox.showerror("错误", f"转换失败: {str(e)}")

# 创建主窗口
root = Tk()
root.title("图片转ICO工具")

# 输入文件选择
Label(root, text="选择图片:").grid(row=0, column=0, padx=5, pady=5)
entry_input = Entry(root, width=40)
entry_input.grid(row=0, column=1, padx=5, pady=5)
Button(root, text="浏览...", command=lambda: entry_input.insert(END, filedialog.askopenfilename(
    filetypes=[("图片文件", "*.jpg *.jpeg *.png")]))).grid(row=0, column=2)

# 输出目录选择
Label(root, text="保存位置:").grid(row=1, column=0, padx=5, pady=5)
entry_output = Entry(root, width=40)
entry_output.grid(row=1, column=1, padx=5, pady=5)
Button(root, text="浏览...", command=lambda: entry_output.insert(END, filedialog.askdirectory())).grid(row=1, column=2)

# 转换按钮
Button(root, text="开始转换", command=convert_to_ico, bg="#4CAF50", fg="white").grid(row=2, column=1, pady=10)

root.mainloop()