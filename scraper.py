import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time

BASE_URL = "https://iresults.net/assam/10/view.php?prefix=B26&roll=0068&no="

START = 103
END = 213

data = []

# 🔥 Extract Marks + Result
def extract_marks(soup):
    total = 0
    result = ""

    rows = soup.select("table.mark-details tr")

    for tr in rows:
        tds = tr.find_all("td")

        if not tds:
            continue

        first = tds[0].get_text(strip=True)

        # Grand Total
        if "Grand Total" in first:
            numbers = [td.get_text(strip=True) for td in tds if td.get_text(strip=True).isdigit()]
            if numbers:
                total = int(numbers[-1])

        # Result
        if "Result" in first:
            result = tds[-1].get_text(strip=True)

    return total, result


# ⭐ Star / Letter detect
def extract_extra(soup):
    star = False
    letter = False

    rows = soup.select("table.mark-details tr")

    for tr in rows:
        text = tr.get_text()

        if "*" in text:
            star = True
        if "L" in text:
            letter = True

    return star, letter


# 🏆 Division detect
def get_division(result):
    if "FIRST" in result:
        return "FIRST"
    elif "SECOND" in result:
        return "SECOND"
    elif "THIRD" in result:
        return "THIRD"
    else:
        return "FAIL"


def scrape(no):
    url = BASE_URL + str(no).zfill(4)

    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Name
        name = soup.find("td", string="Name")
        name = name.find_next("td").text.strip() if name else ""

        # Father
        father = soup.find("td", string="Father's Name")
        father = father.find_next("td").text.strip() if father else ""

        # Mother
        mother = soup.find("td", string="Mother's Name")
        mother = mother.find_next("td").text.strip() if mother else ""

        # Marks + Result
        total, result = extract_marks(soup)

        percent = round((total / 600) * 100, 2) if total else 0

        # Status
        status = "PASS" if "DIVISION" in result else "FAIL"

        # ⭐ Extra
        star, letter = extract_extra(soup)

        # 🏆 Division
        division = get_division(result)

        return {
            "roll": str(no).zfill(4),
            "name": name,
            "father": father,
            "mother": mother,
            "marks": total,
            "percent": percent,
            "result": result,
            "status": status,
            "division": division,
            "star": star,
            "letter": letter
        }

    except Exception as e:
        print(f"❌ Error {no}: {e}")
        return None


# 🔥 RUN
for i in range(START, END + 1):
    d = scrape(i)

    if d:
        print(f"✔ {d['roll']} | {d['name']} | {d['marks']}")
        data.append(d)

    time.sleep(0.5)


# 🔥 SORT + RANK
data = sorted(data, key=lambda x: x["marks"], reverse=True)

for i, d in enumerate(data):
    d["rank"] = i + 1


# 🔥 TOPPER
if data:
    print("\n🔥 TOPPER:", data[0]["name"], data[0]["marks"])


# 🔥 SAVE JSON
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


# 🔥 SAVE EXCEL
df = pd.DataFrame(data)
df.to_excel("results.xlsx", index=False)


# 🔥 TOP 10
print("\n🏆 TOP 10:")
for d in data[:10]:
    print(f"{d['rank']}. {d['name']} - {d['marks']}")
