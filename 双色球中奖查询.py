import tkinter as tk
from tkinter import messagebox, ttk
import re
import requests
from bs4 import BeautifulSoup

class LotteryChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("彩票查询工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置字体支持中文
        self.font = ('SimHei', 10)
        
        # 缓存最近20期完整数据（包含期号和开奖号码）
        self.recent_data = {
            "dlt": [],  # 大乐透最近数据，格式: [{"issue": "2025076", "front": [1,2,3,4,5], "back": [6,7]}, ...]
            "ssq": []   # 双色球最近数据，格式: [{"issue": "2025076", "red": [1,2,3,4,5,6], "blue": 7}, ...]
        }
        
        # 创建界面
        self.create_widgets()
        
        # 当前选中的彩票类型
        self.current_type = None
        
        # 网站基础URL
        self.base_urls = {
            "dlt": "https://kaijiang.78500.cn/dlt/",        # 大乐透列表页
            "ssq": "https://kaijiang.78500.cn/ssq/"         # 双色球列表页
        }
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建顶部按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 大乐透按钮
        self.dlt_button = tk.Button(
            button_frame, 
            text="大乐透查询", 
            command=lambda: self.show_input_form("dlt"),
            width=15, 
            height=2,
            font=self.font
        )
        self.dlt_button.grid(row=0, column=0, padx=10)
        
        # 双色球按钮
        self.ssq_button = tk.Button(
            button_frame, 
            text="双色球查询", 
            command=lambda: self.show_input_form("ssq"),
            width=15, 
            height=2,
            font=self.font
        )
        self.ssq_button.grid(row=0, column=1, padx=10)
        
        # 创建输入框架（初始隐藏）
        self.input_frame = tk.Frame(self.root)
        
        # 期数选择区域（初始隐藏，爬取完成后显示）
        self.issue_frame = tk.Frame(self.input_frame)
        tk.Label(self.issue_frame, text="请选择期号:", font=self.font).grid(row=0, column=0, sticky="w", pady=5)
        self.issue_var = tk.StringVar()
        self.issue_combobox = ttk.Combobox(
            self.issue_frame, 
            textvariable=self.issue_var, 
            width=18, 
            font=self.font,
            state="readonly"  # 设置为只读，只能选择
        )
        self.issue_combobox.grid(row=0, column=1, pady=5)
        self.issue_frame.pack_forget()  # 初始隐藏期号选择框
        
        # 号码输入区域（动态创建）
        self.number_frames = {}
        
        # 大乐透号码输入
        dlt_frame = tk.Frame(self.input_frame)
        tk.Label(dlt_frame, text="前区号码 (5个，空格分隔):", font=self.font).grid(row=0, column=0, sticky="w", pady=5)
        self.dlt_front_entry = tk.Entry(dlt_frame, width=30, font=self.font)
        self.dlt_front_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(dlt_frame, text="后区号码 (2个，空格分隔):", font=self.font).grid(row=1, column=0, sticky="w", pady=5)
        self.dlt_back_entry = tk.Entry(dlt_frame, width=30, font=self.font)
        self.dlt_back_entry.grid(row=1, column=1, pady=5)
        
        self.number_frames["dlt"] = dlt_frame
        
        # 双色球号码输入
        ssq_frame = tk.Frame(self.input_frame)
        tk.Label(ssq_frame, text="红球号码 (6个，空格分隔):", font=self.font).grid(row=0, column=0, sticky="w", pady=5)
        self.ssq_red_entry = tk.Entry(ssq_frame, width=30, font=self.font)
        self.ssq_red_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(ssq_frame, text="蓝球号码 (1个):", font=self.font).grid(row=1, column=0, sticky="w", pady=5)
        self.ssq_blue_entry = tk.Entry(ssq_frame, width=30, font=self.font)
        self.ssq_blue_entry.grid(row=1, column=1, pady=5)
        
        self.number_frames["ssq"] = ssq_frame
        
        # 查询按钮
        self.query_button = tk.Button(
            self.input_frame, 
            text="查询", 
            command=self.check_result,
            width=10,
            font=self.font
        )
        self.query_button.pack_forget()  # 初始隐藏查询按钮
        
        # 状态标签（用于显示爬取进度）
        self.status_label = tk.Label(self.input_frame, text="", font=self.font, fg="blue")
        self.status_label.pack(pady=10)
        
        # 调试信息标签
        self.debug_label = tk.Label(self.input_frame, text="", font=('SimHei', 8), fg="gray")
        self.debug_label.pack(pady=5)
        
        # 结果显示区域
        self.result_frame = tk.Frame(self.root)
        self.result_text = tk.Text(self.result_frame, height=15, width=80, font=self.font)
        self.result_text.pack(pady=10)
        self.result_text.config(state=tk.DISABLED)
    
    def show_input_form(self, lottery_type):
        """显示对应彩票类型的输入表单，并爬取最近20期完整数据"""
        self.current_type = lottery_type
        
        # 显示输入框架
        self.input_frame.pack(pady=10)
        
        # 隐藏所有号码输入框架
        for frame in self.number_frames.values():
            frame.pack_forget()
        
        # 显示选中的号码输入框架
        self.number_frames[lottery_type].pack(pady=10)
        
        # 清空输入框
        if lottery_type == "dlt":
            self.dlt_front_entry.delete(0, tk.END)
            self.dlt_back_entry.delete(0, tk.END)
        else:
            self.ssq_red_entry.delete(0, tk.END)
            self.ssq_blue_entry.delete(0, tk.END)
        
        # 清空结果区域
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # 隐藏期号选择框和查询按钮，显示状态标签
        self.issue_frame.pack_forget()
        self.query_button.pack_forget()
        self.status_label.config(text=f"正在获取{['大乐透', '双色球'][lottery_type == 'ssq']}最近20期数据...", fg="blue")
        self.debug_label.config(text="")  # 清空调试信息
        self.root.update()  # 更新界面显示
        
        # 检查是否已有缓存的期号数据，如果没有则爬取
        if not self.recent_data[lottery_type]:
            # 爬取最近20期完整数据（包含期号和开奖号码）
            success, error = self.crawl_recent_data(lottery_type)
            if error:
                self.status_label.config(text=f"获取数据失败: {error}", fg="red")
                self.debug_label.config(text=f"调试信息: {error}")
            else:
                self._show_issue_combobox()  # 爬取成功后显示期号选择框
        else:
            # 使用缓存的期号数据
            self._show_issue_combobox()
    
    def _show_issue_combobox(self):
        """显示期号选择框并加载数据"""
        # 隐藏状态标签，显示期号选择框和查询按钮
        self.status_label.pack_forget()
        self.issue_frame.pack(pady=5)
        self.query_button.pack(pady=15)
        
        # 提取期号列表用于下拉选择
        issues = [item["issue"] for item in self.recent_data[self.current_type]]
        self.issue_combobox['values'] = issues
        if issues:
            self.issue_var.set(issues[0])  # 默认选择第一期
        
        # 显示成功状态
        self.status_label.config(text=f"已成功获取最近{len(issues)}期数据", fg="green")
        self.status_label.pack(pady=5)
    
    def crawl_recent_data(self, lottery_type):
        """爬取最近20期的完整数据（针对双色球单独优化）"""
        try:
            # 获取列表页URL
            list_url = self.base_urls[lottery_type]
            
            # 设置请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # 发送请求
            response = requests.get(list_url, headers=headers, timeout=10)
            response.encoding = response.apparent_encoding
            
            if response.status_code != 200:
                return False, f"网页访问失败，状态码: {response.status_code}"
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找开奖结果表格（使用独立爬取代码中的选择器）
            table_class = "kjls" if lottery_type == "dlt" else "kj-list-tab"
            table = soup.find('table', class_=table_class)
            
            if not table:
                return False, f"未找到开奖结果表格（class={table_class}）"
            
            # 提取表格行数据
            rows = table.find_all('tr')
            data_list = []
            row_count = 0  # 记录处理的行数
            
            # 跳过表头行，从数据行开始提取
            start_row = 2  # 独立版代码中使用的起始行
            for row in rows[start_row:]:
                cols = row.find_all('td')
                row_count += 1
                
                # 检查列数是否足够
                if len(cols) < 3:
                    self.debug_label.config(text=f"跳过不完整行（列数不足）: 第{row_count}行，列数={len(cols)}")
                    continue
                
                # 提取期号（第一列）
                issue = cols[0].text.strip()
                if not issue.isdigit():
                    self.debug_label.config(text=f"跳过期号无效行: 第{row_count}行，期号={issue}")
                    continue
                
                # 根据彩票类型选择不同的列索引和提取方式
                if lottery_type == "dlt":
                    # 大乐透处理逻辑（使用第四列，索引3）
                    if len(cols) >= 4:
                        numbers_cell = cols[3]
                        numbers_text = numbers_cell.text.strip()
                        numbers = re.findall(r'\d+', numbers_text)
                        
                        if len(numbers) == 7:
                            front_numbers = [int(num) for num in numbers[:5]]
                            back_numbers = [int(num) for num in numbers[5:7]]
                            
                            data_list.append({
                                "issue": issue,
                                "front": sorted(front_numbers),
                                "back": sorted(back_numbers)
                            })
                        else:
                            self.debug_label.config(text=f"大乐透号码数量不符: 第{row_count}行，提取到{len(numbers)}个数字")
                    else:
                        self.debug_label.config(text=f"大乐透号码列不存在: 第{row_count}行，列数={len(cols)}")
                
                else:  # 双色球处理逻辑（使用独立爬取代码中的方法）
                    # 双色球使用第三列（索引2）- 与独立版代码保持一致
                    if len(cols) >= 3:
                        numbers_cell = cols[2]
                        
                        # 优先尝试独立版代码中的标签提取法
                        red_balls = numbers_cell.find_all('span', class_='red')
                        blue_ball = numbers_cell.find('span', class_='blue')
                        
                        if red_balls and blue_ball and len(red_balls) == 6:
                            # 使用标签提取成功
                            red_numbers = [int(ball.text.strip()) for ball in red_balls]
                            blue_number = int(blue_ball.text.strip())
                            
                            data_list.append({
                                "issue": issue,
                                "red": sorted(red_numbers),
                                "blue": blue_number
                            })
                        else:
                            # 标签提取失败，回退到文本提取法
                            numbers_text = numbers_cell.text.strip()
                            numbers = re.findall(r'\d+', numbers_text)
                            
                            if len(numbers) == 7:
                                red_numbers = [int(num) for num in numbers[:6]]
                                blue_number = int(numbers[6])
                                
                                data_list.append({
                                    "issue": issue,
                                    "red": sorted(red_numbers),
                                    "blue": blue_number
                                })
                            else:
                                self.debug_label.config(text=f"双色球号码提取失败: 第{row_count}行，标签提取={len(red_balls) if red_balls else 0}个红球, 文本提取={len(numbers)}个数字")
                    else:
                        self.debug_label.config(text=f"双色球号码列不存在: 第{row_count}行，列数={len(cols)}")
                
                # 只取最近20期
                if len(data_list) >= 20:
                    break
            
            if not data_list:
                return False, "未提取到有效开奖数据，请检查网页结构是否变化"
                
            # 按期号降序排序（最新的在前）
            data_list.sort(key=lambda x: x["issue"], reverse=True)
            
            # 保存到缓存
            self.recent_data[lottery_type] = data_list
            
            return True, None
            
        except Exception as e:
            return False, f"爬取数据失败: {str(e)}"
    
    def get_lottery_data_from_cache(self, issue):
        """从缓存中获取指定期号的开奖数据"""
        for item in self.recent_data[self.current_type]:
            if item["issue"] == issue:
                return item
        return None
    
    def validate_input(self):
        """验证用户输入"""
        issue = self.issue_var.get().strip()
        if not issue:
            messagebox.showwarning("警告", "请选择期号")
            return False
        
        if self.current_type == "dlt":
            front_numbers = self.dlt_front_entry.get().strip()
            back_numbers = self.dlt_back_entry.get().strip()
            
            if not front_numbers or not back_numbers:
                messagebox.showwarning("警告", "请输入完整的号码")
                return False
                
            # 验证前区号码 (5个1-35的数字，不重复)
            front_list = re.findall(r'\d+', front_numbers)
            if len(front_list) != 5:
                messagebox.showwarning("警告", "前区号码必须是5个数字")
                return False
                
            try:
                front_list = [int(num) for num in front_list]
                for num in front_list:
                    if num < 1 or num > 35:
                        raise ValueError
                if len(set(front_list)) != 5:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", "前区号码格式错误，必须是5个1-35的不重复数字")
                return False
                
            # 验证后区号码 (2个1-12的数字，不重复)
            back_list = re.findall(r'\d+', back_numbers)
            if len(back_list) != 2:
                messagebox.showwarning("警告", "后区号码必须是2个数字")
                return False
                
            try:
                back_list = [int(num) for num in back_list]
                for num in back_list:
                    if num < 1 or num > 12:
                        raise ValueError
                if len(set(back_list)) != 2:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", "后区号码格式错误，必须是2个1-12的不重复数字")
                return False
                
            return {
                "issue": issue,
                "front": sorted(front_list),
                "back": sorted(back_list)
            }
            
        else:  # 双色球
            red_numbers = self.ssq_red_entry.get().strip()
            blue_number = self.ssq_blue_entry.get().strip()
            
            if not red_numbers or not blue_number:
                messagebox.showwarning("警告", "请输入完整的号码")
                return False
                
            # 验证红球号码 (6个1-33的数字，不重复)
            red_list = re.findall(r'\d+', red_numbers)
            if len(red_list) != 6:
                messagebox.showwarning("警告", "红球号码必须是6个数字")
                return False
                
            try:
                red_list = [int(num) for num in red_list]
                for num in red_list:
                    if num < 1 or num > 33:
                        raise ValueError
                if len(set(red_list)) != 6:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", "红球号码格式错误，必须是6个1-33的不重复数字")
                return False
                
            # 验证蓝球号码 (1个1-16的数字)
            try:
                blue_num = int(blue_number)
                if blue_num < 1 or blue_num > 16:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", "蓝球号码格式错误，必须是1个1-16的数字")
                return False
                
            return {
                "issue": issue,
                "red": sorted(red_list),
                "blue": blue_num
            }
    
    def check_dlt_winning(self, user_numbers, winning_numbers):
        """判断大乐透中奖等级"""
        # 计算前区匹配数
        front_match = len(set(user_numbers['front']) & set(winning_numbers['front']))
        # 计算后区匹配数
        back_match = len(set(user_numbers['back']) & set(winning_numbers['back']))
        
        # 判断中奖等级
        if front_match == 5 and back_match == 2:
            return ("一等奖", "10000000元")  # 简化处理，实际需根据奖池判断
        elif front_match == 5 and back_match == 1:
            return ("二等奖", "5000000元")   # 简化处理
        elif front_match == 5 and back_match == 0:
            return ("三等奖", "10000元")
        elif front_match == 4 and back_match == 2:
            return ("四等奖", "3000元")
        elif front_match == 4 and back_match == 1:
            return ("五等奖", "300元")
        elif front_match == 3 and back_match == 2:
            return ("六等奖", "200元")
        elif front_match == 4 and back_match == 0:
            return ("七等奖", "100元")
        elif front_match == 3 and back_match == 1:
            return ("八等奖", "15元")
        elif front_match == 2 and back_match == 2:
            return ("八等奖", "15元")
        elif front_match == 3 and back_match == 0:
            return ("九等奖", "5元")
        elif front_match == 1 and back_match == 2:
            return ("九等奖", "5元")
        elif front_match == 2 and back_match == 1:
            return ("九等奖", "5元")
        elif front_match == 0 and back_match == 2:
            return ("九等奖", "5元")
        else:
            return ("未中奖", "0元")
    
    def check_ssq_winning(self, user_numbers, winning_numbers):
        """判断双色球中奖等级"""
        # 计算红球匹配数
        red_match = len(set(user_numbers['red']) & set(winning_numbers['red']))
        # 计算蓝球是否匹配
        blue_match = 1 if user_numbers['blue'] == winning_numbers['blue'] else 0
        
        # 判断中奖等级
        if red_match == 6 and blue_match == 1:
            return ("一等奖", "10000000元")  # 简化处理，实际需根据奖池判断
        elif red_match == 6 and blue_match == 0:
            return ("二等奖", "5000000元")   # 简化处理
        elif red_match == 5 and blue_match == 1:
            return ("三等奖", "3000元")
        elif (red_match == 5 and blue_match == 0) or (red_match == 4 and blue_match == 1):
            return ("四等奖", "200元")
        elif (red_match == 4 and blue_match == 0) or (red_match == 3 and blue_match == 1):
            return ("五等奖", "10元")
        elif blue_match == 1:
            return ("六等奖", "5元")
        else:
            return ("未中奖", "0元")
    
    def highlight_numbers(self, user_nums, winning_nums):
        """生成高亮显示的号码文本"""
        result = []
        
        if self.current_type == "dlt":
            # 处理大乐透号码
            result.append("您的号码:")
            result.append("前区: " + ", ".join([
                f"【{num}】" if num in winning_nums['front'] else f"{num}" 
                for num in user_nums['front']
            ]))
            result.append("后区: " + ", ".join([
                f"【{num}】" if num in winning_nums['back'] else f"{num}" 
                for num in user_nums['back']
            ]))
            result.append("\n开奖号码:")
            result.append("前区: " + ", ".join(map(str, winning_nums['front'])))
            result.append("后区: " + ", ".join(map(str, winning_nums['back'])))
        else:
            # 处理双色球号码
            result.append("您的号码:")
            result.append("红球: " + ", ".join([
                f"【{num}】" if num in winning_nums['red'] else f"{num}" 
                for num in user_nums['red']
            ]))
            result.append(f"蓝球: {'【' + str(user_nums['blue']) + '】' if user_nums['blue'] == winning_nums['blue'] else str(user_nums['blue'])}")
            result.append("\n开奖号码:")
            result.append("红球: " + ", ".join(map(str, winning_nums['red'])))
            result.append(f"蓝球: {winning_nums['blue']}")
            
        return "\n".join(result)
    
    def check_result(self):
        """查询并显示结果（使用本地缓存数据，不再次访问网页）"""
        # 验证输入
        user_input = self.validate_input()
        if not user_input:
            return
            
        # 从缓存中获取开奖数据（不再访问网页）
        winning_data = self.get_lottery_data_from_cache(user_input['issue'])
        if not winning_data:
            messagebox.showinfo("结果", f"未找到{user_input['issue']}期的开奖数据")
            return
            
        # 判断中奖等级
        if self.current_type == "dlt":
            winning_level, prize = self.check_dlt_winning(user_input, winning_data)
        else:
            winning_level, prize = self.check_ssq_winning(user_input, winning_data)
        
        # 生成高亮显示的号码文本
        highlighted_text = self.highlight_numbers(user_input, winning_data)
        
        # 显示结果
        result_text = f"期号: {user_input['issue']}\n\n{highlighted_text}\n\n中奖结果: {winning_level}\n奖金: {prize}"
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)
        
        # 高亮显示（使用【】标记中奖数字）
        self.result_text.config(state=tk.DISABLED)
        self.result_frame.pack(pady=10)
        
        # 弹窗显示结果
        messagebox.showinfo("查询结果", f"{winning_level}\n奖金: {prize}")

if __name__ == "__main__":
    # 注意：实际运行需要确保以下库已安装：
    # pip install requests beautifulsoup4
    root = tk.Tk()
    app = LotteryChecker(root)
    root.mainloop()