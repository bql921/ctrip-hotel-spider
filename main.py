import pipline
import playwrightCheck
import saveInfo


if __name__ == "__main__":
    if not playwrightCheck.check_playwright_environment():
        print("Playwright 环境检查未通过，程序终止。")
        exit(1)

    if (
        not playwrightCheck.check_login_by_cookies()
        or not playwrightCheck.check_login_realtime()
    ):
        print("\n当前未检测到有效登录状态。")
        print("是否需要手动登录携程网站？(y/n)")
        need_login = input().strip().lower()
        if need_login == "y":
            playwrightCheck.manual_login_procedure()
        else:
            print("⚠️  未登录状态下，部分数据可能无法获取。")

    print("请输入酒店ID：")
    hotel_id = input().strip()
    hotel_name = saveInfo.get_hotel_name(hotel_id)
    print("请确认酒店ID为：" + hotel_id + ", 酒店名称为：" + hotel_name + "，是否继续？(y/n)")
    confirm = input().strip().lower()
    if confirm == "y":
        pipline.pipline(hotel_id)
    else:
        print("操作已取消。")
