from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions()
# 启用无头模式
# co.set_argument('--headless')   # 开启无头模式
# 或禁用无头模式（让浏览器窗口可见）
# co.remove_argument('--headless')
page = ChromiumPage(co)
page.get('https://byr.pt/')