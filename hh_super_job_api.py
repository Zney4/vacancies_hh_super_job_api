from itertools import count
import time
import requests
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def hh_request_predict_rub_salary(lang, url, page=0):
    payload = {
        "area": "1",
        "page": page,
        "text": f"Программист {lang}",
        "only_with_salary": True,
    }
    time.sleep(0.3)
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_superjob_vacancies(api_key, lang, page=0):
    period_in_days = 30
    catalogue_count = 48
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {"X-Api-App-Id": api_key}
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


def hh_predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        hh_salary_calculation = int((salary_to + salary_from) / 2)
    elif salary_from:
        hh_salary_calculation = int(1.2 * salary_from)
    elif salary_to:
        hh_salary_calculation = int(0.8 * salary_to)
    else:
        print("None")
    return hh_salary_calculation


def job_predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        return int((salary_to + salary_from) / 2)
    elif salary_from:
        return int(1.2 * salary_from)
    elif salary_to:
        return int(0.8 * salary_to)
    return None


def job_request_and_result(list_language):
    job_vacancies_by_language = {}

    for lang in list_language:
        salaries = []
        total_vacancies = 0

        for page in count(0):
            job_vacancies = get_superjob_vacancies(API_KEY, lang, page)
            job_total_vacancies = job_vacancies.get("total", 0)
            job_vacancies = job_vacancies.get("objects", [])
            if not job_vacancies:
                break

            for vacancy in job_vacancies:
                if vacancy.get("currency") != "rub":
                    continue

                salary = job_predict_rub_salary(
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


def hh_get_list_vacancies(page=0):
    for lang in list_language:

        salary_by_vacancies = []
        for page in count(0):
            payload = {
                "area": "1",
                "text": f"Программист {lang}",
                "page": page,
                "only_with_salary": True,
            }
            time.sleep(0.3)
            response = requests.get(url, params=payload)
            response.raise_for_status()
            count_total_vacancies = response.json()

            if page >= count_total_vacancies["pages"] - 1:
                break

        for page in count(0):
            vacancies = hh_request_predict_rub_salary(lang, url, page=page)
            if page >= vacancies["pages"] - 1:
                break

            for vacancy in vacancies["items"]:
                salary = vacancy.get("salary")
                if salary and salary.get("currency") == "RUR":
                    predicted_salary = hh_predict_rub_salary(
                        salary.get("from"), salary.get("to")
                    )
                    if predicted_salary is not None:
                        salary_by_vacancies.append(predicted_salary)

        average_salary = None
        if salary_by_vacancies:
            average_salary = int(sum(salary_by_vacancies) / len(salary_by_vacancies))

        vacancies_by_language[lang] = {
            "vacancies_found": count_total_vacancies.get("found"),
            "vacancies_processed": len(salary_by_vacancies),
            "average_salary": average_salary,
        }

    return vacancies_by_language


def hh_create_table(title, hh_statistics):
    table_contents = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]

    for language, vacancsies in hh_statistics.items():
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


def job_create_table(title, job_statistics):
    table_contents = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]

    for language, vacancsies in job_statistics.items():
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
    API_KEY = os.environ["API_KEY"]
    list_language = [
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
    averages_salarys = []
    TITLE = "HeadHunter Moscow"
    SJ_TITLE = "SuperJob Moscow"
    vacancies_by_language = {}
    list_total_vacancies = []
    url = "https://api.hh.ru/vacancies"

    job_statistics = job_request_and_result(list_language)
    hh_statistics = hh_get_list_vacancies()
    print(hh_create_table(TITLE, hh_statistics))
    print(job_create_table(SJ_TITLE, job_statistics))
