if __name__ == "__main__":
    from random import choice

    from __init__ import session_id
    from api import Lottery
    from check_in.api import JuejinSession

    lottery = Lottery(JuejinSession(session_id))
    lottery_config = lottery.get_config()
    # You will get a free draw every day after check-in
    for _ in range(lottery_config["free_count"]):
        # By default, it only draw a lottery when it does not cost any points
        result = lottery.draw()
        print("You win a", result['lottery_name'])

    lottery_history = lottery.get_history()["lotteries"]
    random_record = choice(lottery_history)["history_id"]
    lottery.attract_luck(random_record)

    luck = lottery.get_luck()["total_value"]
    print(f"\nYour luck is {luck}. {'Claim your prize right now!' if luck >= 6000 else ''}")
