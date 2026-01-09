import pipline
import subprocess
import sys
import os
from playwright.sync_api import sync_playwright
import inheritChromeInfo
import json

def check_playwright_installation():
    """检查 Playwright 浏览器是否已安装"""
    try:
        # 方法1: 检查 playwright 命令是否可用
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            print("⚠️  Playwright 未正确安装")
            return False

        print(f"✓ Playwright 版本: {result.stdout.strip()}")

        # 方法2: 检查浏览器是否已安装
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # 如果输出包含 "is already installed"，说明浏览器已安装
        if "is already installed" in result.stdout or result.returncode == 0:
            print("✓ Chromium 浏览器已安装")
            return True
        else:
            print("⚠️  Chromium 浏览器未安装或版本不匹配")
            print(f"输出: {result.stdout}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  检查超时")
        return False
    except FileNotFoundError:
        print("⚠️  未找到 Playwright，请先安装: pip install playwright")
        return False
    except Exception as e:
        print(f"⚠️  检查 Playwright 时出错: {e}")
        return False


def check_browser_path():
    """检查浏览器文件是否存在"""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # 获取浏览器可执行文件路径
            browser_path = p.chromium.executable_path

            if os.path.exists(browser_path):
                print(f"✓ 浏览器路径存在: {browser_path}")
                return True
            else:
                print(f"✗ 浏览器路径不存在: {browser_path}")
                return False

    except Exception as e:
        print(f"✗ 无法获取浏览器路径: {e}")
        return False


def install_playwright_browsers():
    """安装 Playwright 浏览器"""
    print("\n正在安装 Playwright 浏览器...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
        )

        if result.returncode == 0:
            print("✓ 浏览器安装成功")
            return True
        else:
            print(f"✗ 浏览器安装失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ 安装过程出错: {e}")
        return False


# 检查流程整合
def check_playwright_environment():
    # 检查 Playwright 安装状态
    print("\n[1/3] 检查 Playwright 环境...")
    playwright_ok = check_playwright_installation()

    print("\n[2/3] 检查浏览器文件...")
    browser_ok = check_browser_path()

    # 如果检查失败，尝试重新安装
    if not playwright_ok or not browser_ok:
        print("\n检测到 Playwright 环境问题，是否重新安装浏览器？(y/n)")
        reinstall = input().strip().lower()

        if reinstall == "y":
            if install_playwright_browsers():
                print("\n重新检查浏览器...")
                browser_ok = check_browser_path()
            else:
                print("\n浏览器安装失败，程序可能无法正常运行")
        else:
            print("\n⚠️  跳过安装，程序可能无法正常运行")

    print("\n[3/3] 环境检查完成。")
    return playwright_ok and browser_ok



def check_login_by_cookies(storage_state_path="ctrip_state.json"):
    """通过检查 Cookie 判断是否已登录"""
    
    # 关键登录 Cookie 名称
    LOGIN_COOKIES = [
        "cticket",      # 携程登录票据
        "login_uid",    # 登录用户ID
        "login_type",   # 登录类型
        "_udl",         # 用户数据
        "AHeadUserInfo" # 用户头部信息
    ]
    
    try:
        # 检查文件是否存在
        if not os.path.exists(storage_state_path):
            print(f"✗ 未找到登录状态文件: {storage_state_path}")
            return False
        
        # 读取 storage state
        with open(storage_state_path, 'r', encoding='utf-8') as f:
            storage_state = json.load(f)
        
        cookies = storage_state.get('cookies', [])
        
        # 检查是否存在关键 Cookie
        found_cookies = {}
        for cookie in cookies:
            cookie_name = cookie.get('name')
            if cookie_name in LOGIN_COOKIES:
                found_cookies[cookie_name] = cookie.get('value', '')
        
        # 判断登录状态
        if 'cticket' in found_cookies and 'login_uid' in found_cookies:
            print("✓ 检测到登录状态")
            print(f"  - 用户ID: {found_cookies.get('login_uid', 'N/A')[:20]}...")
            print(f"  - 登录票据: {found_cookies.get('cticket', 'N/A')[:20]}...")
            
            # 检查 Cookie 是否过期
            for cookie in cookies:
                if cookie.get('name') == 'cticket':
                    expires = cookie.get('expires', 0)
                    if expires > 0:
                        import time
                        if expires < time.time():
                            print("  ⚠️  登录票据已过期，可能需要重新登录")
                            return False
            
            return True
        else:
            print("✗ 未检测到有效的登录 Cookie")
            missing = [c for c in LOGIN_COOKIES if c not in found_cookies]
            print(f"  缺少: {', '.join(missing[:3])}")
            return False
            
    except json.JSONDecodeError:
        print(f"✗ 登录状态文件格式错误: {storage_state_path}")
        return False
    except Exception as e:
        print(f"✗ 检查登录状态时出错: {e}")
        return False

def check_login_realtime():
    """实时访问网站检查登录状态"""
    try:
        with sync_playwright() as p:
            print("\n正在实时检查登录状态...")
            
            # 加载已保存的登录状态
            browser = p.chromium.launch(headless=True)
            
            if os.path.exists("ctrip_state.json"):
                context = browser.new_context(storage_state="ctrip_state.json")
            else:
                context = browser.new_context()
            
            page = context.new_page()
            page.goto("https://hotels.ctrip.com/", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # 获取当前页面的 Cookie
            cookies = context.cookies()
            
            # 检查关键 Cookie
            has_cticket = any(c.get('name') == 'cticket' for c in cookies)
            has_login_uid = any(c.get('name') == 'login_uid' for c in cookies)
            
            browser.close()
            
            if has_cticket and has_login_uid:
                print("✓ 实时检查: 已登录")
                return True
            else:
                print("✗ 实时检查: 未登录")
                return False
                
    except Exception as e:
        print(f"✗ 实时检查失败: {e}")
        return False

def display_login_info(storage_state_path="ctrip_state.json"):
    """显示详细的登录信息"""
    try:
        with open(storage_state_path, 'r', encoding='utf-8') as f:
            storage_state = json.load(f)
        
        cookies = storage_state.get('cookies', [])
        
        print("\n" + "=" * 60)
        print("登录状态详情")
        print("=" * 60)
        
        important_cookies = {
            'cticket': '登录票据',
            'login_uid': '用户ID',
            'login_type': '登录类型',
            'AHeadUserInfo': '用户信息',
            'DUID': '设备ID'
        }
        
        for cookie in cookies:
            name = cookie.get('name')
            if name in important_cookies:
                value = cookie.get('value', '')
                expires = cookie.get('expires', 0)
                
                print(f"\n{important_cookies[name]} ({name}):")
                print(f"  值: {value[:50]}{'...' if len(value) > 50 else ''}")
                
                if expires > 0:
                    import time
                    import datetime
                    expire_time = datetime.datetime.fromtimestamp(expires)
                    is_valid = expires > time.time()
                    status = "有效" if is_valid else "已过期"
                    print(f"  过期时间: {expire_time} ({status})")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"无法显示登录信息: {e}")
    
def manual_login_procedure():
    """引导用户手动登录携程"""
    print("\n请在打开的浏览器中手动登录携程网站。")
    print("登录完成后，返回此窗口并按回车继续...")
    inheritChromeInfo.inherit_chrome_info()
    print("✓ 登录信息已保存。")
    


if __name__ == "__main__":
    # print("=" * 60)
    # print("携程酒店信息爬虫")
    # print("=" * 60)

    # # 检查 Playwright 安装状态
    # print("\n[1/3] 检查 Playwright 环境...")
    # playwright_ok = check_playwright_installation()

    # print("\n[2/3] 检查浏览器文件...")
    # browser_ok = check_browser_path()

    # # 如果检查失败，尝试重新安装
    # if not playwright_ok or not browser_ok:
    #     print("\n检测到 Playwright 环境问题，是否重新安装浏览器？(y/n)")
    #     reinstall = input().strip().lower()

    #     if reinstall == "y":
    #         if install_playwright_browsers():
    #             print("\n重新检查浏览器...")
    #             browser_ok = check_browser_path()
    #         else:
    #             print("\n浏览器安装失败，程序可能无法正常运行")
    #     else:
    #         print("\n⚠️  跳过安装，程序可能无法正常运行")

    # print("\n[3/3] 开始爬取流程...")
    # print("-" * 60)

    if not check_login_by_cookies() or not check_login_realtime():
        print("\n当前未检测到有效登录状态。")
        print("是否需要手动登录携程网站？(y/n)")
        need_login = input().strip().lower()
        if need_login == "y":
            manual_login_procedure()
        else:
            print("⚠️  未登录状态下，部分数据可能无法获取。")

    # print("请输入酒店ID：")
    # hotel_id = input().strip()
    # print(f"请确认酒店ID为：{hotel_id}，是否继续？(y/n)")
    # confirm = input().strip().lower()

    # if confirm == "y":
    #     try:
    #         pipline.pipline(hotel_id)
    #         print("\n" + "=" * 60)
    #         print("✓ 爬取完成！")
    #         print("=" * 60)
    #     except Exception as e:
    #         print(f"\n✗ 爬取过程出错: {e}")
    #         import traceback
    #         traceback.print_exc()
    # else:
    #     print("操作已取消。")
