import schedule

from action_handler import reminder


def job():
    reminder()


if __name__ == '__main__':
    schedule.every(10).minutes.do(job)

    while True:
        schedule.run_pending()
