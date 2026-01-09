from playwright.sync_api import sync_playwright

def inherit_chrome_info():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://hotels.ctrip.com")

        print("👉 请手动完成登录，然后在终端内回车")
        input()

        context.storage_state(path="ctrip_state.json")
        

if __name__ == "__main__":
    inherit_chrome_info()
