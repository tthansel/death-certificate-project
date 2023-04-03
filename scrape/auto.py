import pyautogui
import pyperclip
import json
import time
NEXT_BUTTON = (229, 249)
COPY_BUTTON = (743, 103)
YEAR_BUTTON = (207,211)
FILM_BUTTONS = [(72, 281), (69, 311), (70, 342), (71, 376), (71, 409), (70, 440), (74, 475), (72, 507), (71, 540), (69, 573), (73, 606), (73, 638), (74, 672), (74, 703), (547, 279), (546, 311), (546, 343), (547, 374), (545, 408), (546, 440), (546, 477), (547, 509), (543, 539), (544, 572), (546, 606), (545, 637), (545, 668)]
ROLL_NUMBER = (120,251)


def click(coords):
    pyautogui.click(x=coords[0], y=coords[1])

screenWidth, screenHeight = pyautogui.size()

def collect_next_record(sleep_time=2):
    click(NEXT_BUTTON)
    time.sleep(sleep_time)
    click(COPY_BUTTON)
    data = pyperclip.paste() 
    return data

def collect_year():
    mode = 'alpha'
    for i,film in enumerate(FILM_BUTTONS):
        records, mode = collect_film(film, mode=mode)
        with open(f'1942-{i:02}.json','w') as outfile:
            for record in records.items():
                outfile.writelines(json.dumps(record)+'\n')

def collect_film(film_button, mode='alpha', county='Cuyahoga'):
    sleep_time = 5
    click(YEAR_BUTTON)
    time.sleep(1)
    click(film_button)
    time.sleep(5)
    records = {}
    end = False
    roll_number = 1
    last_match = 1
    last_record_number = None
    retry = 0
    good_count = 0
    adams_counter = 0
    highest_roll_number = 0
    while not end:
        data = collect_next_record(sleep_time)
        roll_number += 1
        print(f'Last Match: {last_match}\nRoll Number:{roll_number}')
        record = json.loads(data)
        try:
            record_numbers = [int(x['Record Number']) for x in record]
            if last_record_number is None or (last_record_number + 1) not in record_numbers:
                record_number = int(record[0]['Record Number'])
            else: # (last_record_number + 1) in record_numbers:
                record_number = last_record_number + 1
        except (KeyError, TypeError, IndexError) as e:
            print(f'Caught Exception {e}')
            record_number = None
        print(record)
        print(f'Record Number: {record_number}')
        if record_number is None:
            true_roll_number = get_roll_number()
            if roll_number > true_roll_number:
                end = True
                break
            continue
        if last_record_number is None or record_number == last_record_number + 1 or record_number == 1:
            if last_record_number is not None and last_record_number != 1 and roll_number > highest_roll_number:
                retry = 0
            good_count += 1
            if good_count >= 50:
                sleep_time /= 1.05
                good_count = 0
            records[roll_number] = record
            last_record_number = record_number
            if record[0]['Death Place'].find("Cuyahoga") >= 0:
                last_match = roll_number
            if record[0]['Death Place'].find("Adams, Ohio") >= 0:
                adams_counter +=1
            else:
                adams_counter = 0
            if mode == 'catchup' and adams_counter > 3:
                mode = 'alpha'
            if roll_number - last_match > 25:
                if mode == 'alpha':
                    increment = 100
                else:
                    continue
                roll_number, mode = start_search(data, roll_number, increment, 'Cuyahoga', sleep=sleep_time, mode=mode)
                last_match = roll_number
                last_record_number = None
        elif record_number == last_record_number:
            records[roll_number] = ['duplicate']
            true_roll_number = get_roll_number()
            print(f"Roll Number: {roll_number}\nTrue roll number: {true_roll_number}")
            if roll_number > true_roll_number:
                end = True
                break
            continue
            #Check for end of roll?
        else:
            #Missing one?
            highest_roll_number = max(roll_number, highest_roll_number)
            if retry >= 3:
                print("Unable to recover from out of sequence")
                sleep_time /= 1.2**3
                roll_number = highest_roll_number
                seek(roll_number)
                last_record_number = None
                retry = 0
                continue
            good_count = 0
            sleep_time *= 1.2
            print(f"Out of sequence, found {record_number}, expected {last_record_number + 1}")
            last_good = last_good_roll_number(records, roll_number)
            roll_number = last_good-retry
            seek(roll_number)
            retry += 1
            continue
    return records, mode

def get_roll_number(depth=0):
    if depth == 3:
        return None
    click(ROLL_NUMBER)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl','a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl','c')
    try:
        roll_number = int(pyperclip.paste())
    except ValueError:
        roll_number = get_roll_number(depth=depth+1)
    return roll_number

def last_good_roll_number(records, roll_number):
    print("Locating last good record")
    for n in range(roll_number-1, 0, -1):
        print(f"{n}:{records.get(n,['duplicate'])}")
        if records.get(n,['duplicate'])[0] != "duplicate":
            return n

def seek(roll_number):
    click(ROLL_NUMBER)
    pyautogui.hotkey('ctrl','a')
    pyautogui.typewrite(str(roll_number))
    pyautogui.hotkey('enter')

def start_search(data, roll_number, increment, target='Cuyahoga', sleep=2, mode='alpha'):
    print('Attempting to fast forward')
    first_data = data
    while data == first_data:
        first_data = collect_next_record(sleep_time=sleep)
        roll_number +=1
    first_record = json.loads(first_data)
    first_location = first_record[0]['Death Place'].split(',')[-2].strip() #Should be the county, for either City, County, State or County, State
    switch_mode = False
    if first_location > target:
        target = 'ZZZ'
        switch_mode = True
    print(f"First Location: {first_location}, target: {target}")
    roll_number, switch_mode = search(first_location, first_data, roll_number, target, increment, sleep=sleep, switch_mode=switch_mode)
    if switch_mode:
        if mode == 'catchup':
            mode = 'alpha'
        else:
            mode = 'catchup'
    return roll_number, mode

def search(last_location, last_data, roll_number, target, increment, sleep=2, switch_mode=False):
    print(f'Roll Number: {roll_number}\nIncrement: {increment}')
    if increment == 1:
        seek(roll_number)
        time.sleep(sleep)
        return (roll_number, switch_mode)
    last_roll_number = roll_number
    roll_number += increment
    seek(roll_number)
    true_roll_number = get_roll_number()
    if true_roll_number < roll_number:
        return search(last_location, last_data, true_roll_number, target, increment//2, sleep=sleep, switch_mode = False)
    time.sleep(2)
    next_data = last_data
    pages = 0
    while next_data == last_data:
        next_data = collect_next_record(sleep_time=sleep)
        pages += 1
        true_roll_number = get_roll_number()
        if roll_number + pages > true_roll_number:
            print("End, back")
            return search(last_location, last_data, last_roll_number, target, increment//2, sleep=sleep, switch_mode=False)
    print(next_data)
    next_record = json.loads(next_data)
    next_location = next_record[0]['Death Place'].split(',')[-2].strip()
    print(f'Next Location: {next_location}')
    if next_location < last_location or next_location >= target:
        print('Back')
        return search(last_location, last_data, last_roll_number, target, increment//2, sleep=sleep, switch_mode = target=='ZZZ')
    elif next_location < target:
        print('Forward')
        return search(next_location, next_data, roll_number, target, increment, sleep=sleep, switch_mode = target=='ZZZ')





if __name__=="__main__":
    collect_year()
