from itertools import count
import time
import requests
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def hh_get_request_vacancies(lang, url, page=0):
    moscow_zone = 1
    payload = {
        "area": f"{moscow_zone}",
        "page": page,
        "text": f"Программист {lang}",
        "only_with_salary": True,
    }
    time.sleep(0.3)
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_superjob_vacancies(super_job_token, lang, page=0):
    period_in_days = 30
    catalogue_count = 48
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {"X-Api-App-Id": super_job_token}
    params = {
        "keyword": f"Программист {lang}",
        "page": page,
        "town": "Москва",
        "period": period_in_days,
        "catalogues": catalogue_count,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def determining_salaries_for_vacancies(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        return int((salary_to + salary_from) / 2)
    elif salary_from:
        return int(1.2 * salary_from)
    elif salary_to:
        return int(0.8 * salary_to)
    return None


def sj_get_statistic_vacancies(super_job_token, languages):
    job_vacancies_by_language = {}

    for lang in language:
        salaries = []
        total_vacancies = 0

        for page in count(0):
            job_vacancies = get_superjob_vacancies(super_job_token, lang, page)
            job_total_vacancies = job_vacancies.get("total", 0)
            job_vacancies = job_vacancies.get("objects", [])
            if not job_vacancies:
                break

            for vacancy in job_vacancies:
                if vacancy.get("currency") != "rub":
                    continue

                salary = determining_salaries_for_vacancies(
                    vacancy.get("payment_from"), vacancy.get("payment_to")
                )

                if salary:
                    salaries.append(salary)

            time.sleep(0.5)

        avg_salary = int(sum(salaries) / len(salaries)) if salaries else 0

        job_vacancies_by_language[lang] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": len(salaries),
            "average_salary": avg_salary,
        }

    return job_vacancies_by_language


def hh_get_statistic_vacancies(moscow_zone, page=0):
    for lang in language:

        salaries_by_vacancies = []
        for page in count(0):
            payload = {
                "area": f"{moscow_zone}",
                "text": f"Программист {lang}",
                "page": page,
                "only_with_salary": True,
            }
            time.sleep(0.3)
            response = requests.get(url, params=payload)
            response.raise_for_status()
            found_count_vacancies = response.json()

            if page >= found_count_vacancies["pages"] - 1:
                break
            vacancies = hh_get_request_vacancies(lang, url, page=page)
            if page >= vacancies["pages"] - 1:
                break

            for vacancy in vacancies["items"]:
                salary = vacancy.get("salary")
                if salary and salary.get("currency") == "RUR":
                    predicted_salary = determining_salaries_for_vacancies(
                        salary.get("from"), salary.get("to")
                    )
                    if predicted_salary:
                        salaries_by_vacancies.append(predicted_salary)

        average_salary = None
        if salaries_by_vacancies:
            average_salary = int(
                sum(salaries_by_vacancies) / len(salaries_by_vacancies)
            )

        vacancies_by_language[lang] = {
            "vacancies_found": found_count_vacancies.get("found"),
            "vacancies_processed": len(salaries_by_vacancies),
            "average_salary": average_salary,
        }

    return vacancies_by_language


def create_table(title, statistics):
    table_contents = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]
    for language, vacancsies in statistics.items():
        table_contents.append(
            [
                language,
                vacancsies["vacancies_found"],
                vacancsies["vacancies_processed"],
                vacancsies["average_salary"],
            ]
        )
    table = AsciiTable(table_contents, title)
    return table.table


if __name__ == "__main__":
    load_dotenv()
    super_job_token = os.environ["SUPER_JOB_TOKEN"]
    hh_title = "HeadHunter Moscow"
    sj_title = "SuperJob Moscow"
    moscow_zone = 1
    language = [
        "JavaScript",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
    ]
    averages_salaries = []
    vacancies_by_language = {}
    total_vacancies = []
    url = "https://api.hh.ru/vacancies"

    job_statistics = sj_get_statistic_vacancies(super_job_token, language)
    hh_statistics = hh_get_statistic_vacancies(moscow_zone)
    hh_table = create_table(hh_title, hh_statistics)
    sj_table = create_table(sj_title, job_statistics)
    print(hh_table)
    print(sj_table)
