import requests

import re

def remove_html_tags(text):
    # Define a regular expression pattern to match HTML tags
    clean = re.compile('<.*?>')
    # Use re.sub to replace the matched patterns with an empty string
    return re.sub(clean, '', text)
def generate_completion(system_prompt: str, prompt: str) -> str:
    url = "http://192.168.31.232:11434/api/generate"  # API endpoint
    model = "qwen2.5:32b"  # Default model
    temperature = 0.7
    max_tokens = 18000


    payload = {
        "model": model,
        "system": system_prompt,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return f"Error: {response.status_code}, {response.text}"

if __name__ == '__main__':
    with open("prompt_tagging.txt", 'r', encoding='utf-8') as f:
        system_prompt = f.read()
        system_prompt = system_prompt.replace("{stock_name}", "SH601127 (赛力斯)")

    prompt = '<p>问界新M7销量破17万，再创新势力销量里程碑该咋看？</p><p>首先，问界新M7销量破17万，再创新势力销量里程碑，这一成就体现了其强大的市场竞争力和消费者认可度。问界新M7凭借其“空间大、开得稳、非常智能、适合家用”的特点，赢得了大量忠实用户的青睐，很多车主甚至主动向身边亲友推荐，形成了良好的口碑效应。这种用户自发的推广，无疑为问界新M7的销量增长注入了强劲的动力。</p><p>其次，问界新M7在智能驾驶和用户体验方面的持续领先，是其销量领跑新势力的关键所在。通过搭载HUAWEI ADS 3.0高阶智能驾驶系统和HarmonyOS 4鸿蒙座舱，问界新M7实现了智慧化、便捷化体验的显著提升。这些创新技术的应用，不仅提高了驾驶的安全</p><img src="https://xqimg.imedao.com/19344fb763e8fa9b3fee9b93.jpg!custom.jpg" class="ke_img" ><p>性和舒适性，也提升了用户的用车体验，从而吸引了更多消费者的关注和购买。</p><p>第三，问界新M7的销量增长还受益于其丰富的产品矩阵和完善的销售网络。问界新M7系列车型包括多个配置和版本，满足了不同消费者的需求。同时，问界在全国范围内建立了大量的体验中心和用户中心，为消费者提供了便捷的购车和售后服务。</p><p>未来，随着新能源汽车市场的不断发展和消费者需求的不断变化，问界新M7有望继续保持领先地位，并带动整个新能源汽车行业的持续发展。<a href="https://xueqiu.com/S/SH601127" target="_blank">$赛力斯(SH601127)$</a> </p>'
    prompt = remove_html_tags(prompt)
    r = generate_completion(system_prompt, prompt)
    print(r)