import os
import re
import requests
import json
import getHotelImages as GHI
import configs
import getHotelComments as GHC
import getHotelDescription as GHD


def recive_name(html_str: str) -> str:
    match = re.search(
        r'<span class="crumbSEO_crumb_content__ikbTo">(.*?)</span>', html_str
    )
    return match.group(1).strip() if match else "未知酒店"


def get_hotel_name(hotel_id):
    hotel_name = ""
    url = f"https://hotels.ctrip.com/hotels/{hotel_id}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        hotel_name = recive_name(response.text)
    return hotel_name


def save_json(hotel_id):
    """获取酒店图片路径并保存为json文件"""
    # 创建json存储目录
    json_dir = os.path.join(configs.HOTEL_INFOS_DIR, f"{hotel_id}.json")
    if not os.path.exists(configs.HOTEL_INFOS_DIR):
        os.makedirs(configs.HOTEL_INFOS_DIR, exist_ok=True)
    # 读取数据并写入json文件
    hotel_name = get_hotel_name(hotel_id)
    hotel_images, user_images, hotel_top_images = GHI.get_hotel_list(hotel_id)
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelName": hotel_name,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "hotel_images": hotel_images,
                "user_images": user_images,
                "hotel_top_images": hotel_top_images,
            },
            f,
            ensure_ascii=False,
            indent=4,
        )


def save_images(hotel_id):
    """下载并保存图片到本地文件夹"""
    # 创建酒店图片存储目录
    hotel_name = get_hotel_name(hotel_id)
    hotel_dir = os.path.join(configs.HOTEL_IMAGES_DIR, f"{hotel_name}_{hotel_id}")
    if not os.path.exists(hotel_dir):
        os.makedirs(hotel_dir, exist_ok=True)

    # 读取json文件
    json_path = os.path.join(configs.HOTEL_INFOS_DIR, f"{hotel_id}.json")
    if not os.path.exists(json_path):
        print(f"JSON file for hotel ID {hotel_id} does not exist.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        hotel_json_data = json.load(f)

    # 酒店图片需要根据category区分存储
    # 有三种类型：hotel_images, user_images, hotel_top_images
    # 每种类型要根据不同categoryName创建子目录
    for category in ["hotel_images", "user_images", "hotel_top_images"]:
        category_dir = os.path.join(hotel_dir, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir, exist_ok=True)

        for img_info in hotel_json_data.get(category, []):
            category_name = img_info.get("categoryName", "无分类")
            category_subdir = os.path.join(category_dir, category_name)
            if not os.path.exists(category_subdir):
                os.makedirs(category_subdir, exist_ok=True)
            for idx, img in enumerate(img_info.get("imgUrlList", [])):
                img_url = img.get("link", "")
                if not img_url:
                    continue
                img_ext = os.path.splitext(img_url)[1].split("?")[0]
                img_filename = f"{category_name}_{idx + 1}{img_ext}"
                img_path = os.path.join(category_subdir, img_filename)

                try_times = 3

                # 下载图片

                # response = requests.get(img_url, timeout=10)
                # response.raise_for_status()
                # with open(img_path, "wb") as img_file:
                #     img_file.write(response.content)
                # print(f"Saved image: {img_path}")
                for attempt in range(try_times):
                    try:
                        response = requests.get(img_url, timeout=10)
                        response.raise_for_status()
                        with open(img_path, "wb") as img_file:
                            img_file.write(response.content)
                        print(f"Saved image: {img_path}")
                        break  # 成功后跳出重试循环
                    except Exception as e:
                        print(
                            f"Attempt {attempt + 1} failed to download image {img_url}: {e}"
                        )
                        if attempt == try_times - 1:
                            print(
                                f"Failed to download image after {try_times} attempts: {img_url}"
                            )


def save_comments(hotel_id, ratingLimit=4.5):
    """获取酒店评论图片并保存为json文件"""
    # 创建json存储目录,跟图片放同一级{hotel_name}_{hotel_id}，然后再创建一个文件夹 存评论json
    # json_dir = os.path.join(configs.HOTEL_IMAGES_DIR, f"{hotel_id}_comments.json")
    comments_dir = os.path.join(
        configs.HOTEL_IMAGES_DIR, f"{get_hotel_name(hotel_id)}_{hotel_id}"
    )
    sub_dir = os.path.join(comments_dir, "comments_and_descriptions")
    json_dir = os.path.join(sub_dir, f"{hotel_id}_comments.json")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir, exist_ok=True)
    # 读取数据并写入json文件
    all_comments = GHC.fetchHotelComments(
        hotel_id, numPages=50, ratingLimit=ratingLimit
    )
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "comments": all_comments,
            },
            f,
            ensure_ascii=False,
            indent=4,
        )


def save_descriptions(hotel_id):
    """获取酒店描述信息并保存为json文件"""
    # 创建路径跟图像片放同一级{hotel_name}_{hotel_id}，然后再创建一个文件夹 存描述json
    descriptions_dir = os.path.join(
        configs.HOTEL_IMAGES_DIR, f"{get_hotel_name(hotel_id)}_{hotel_id}"
    )
    sub_dir = os.path.join(descriptions_dir, "comments_and_descriptions")
    json_dir = os.path.join(sub_dir, f"{hotel_id}_description.json")
    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir, exist_ok=True)
    # 用宽松的函数
    description = GHD.get_hotel_description_relaxed(hotel_id)
    with open(json_dir, "w", encoding="utf-8") as f:
        json.dump(
            {
                "hotelId": hotel_id,
                "hotelURL": f"https://hotels.ctrip.com/hotels/{hotel_id}.html",
                "description": description,
            },
            f,
            ensure_ascii=False,
            indent=4,
        )


if __name__ == "__main__":
    hotel_id = 9532016
    # hotel_name = get_hotel_name(hotel_id)
    # print(f"Hotel Name: {hotel_name}")
    # save_json(hotel_id)
    # save_images(hotel_id)
    # save_comments(hotel_id, ratingLimit=4.5)
    save_descriptions(hotel_id)
