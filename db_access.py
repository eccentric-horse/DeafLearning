import os
import json
import xlsxwriter

from azure.data.tables import TableServiceClient
from datetime import timezone, timedelta

# constants dictating headers for the spreadsheets "answer", "chat log", "survey", and "qa_summary"
answer_headers = ["Question", "Type", "Number of Attempts", "First Attempt Correct?", "Time to Answer",
                  "QA Pop-Up Timestamp"]
chat_log_headers = ["User Message", "Chatbot Message"]
survey_headers = ["Survey Question", "QA Type", "User Rating"]
qa_summary_headers = ["# Transcript", "# Emotion", "# Visual"]

# Survey questions constant
survey_questions = {"q1": "Question 1: Overall, This set of questions help me learn the video better by \"Reducing "
                    "Irrelevant Information\"",
                    "q2": "Question 2: Overall, This set of questions help me learn the video better by \"Focusing "
                    "on Essential Information\"",
                    "q3": "Question 3: Overall, This set of questions help me learn the video better by \"Fostering"
                    " Connection between Test and Image\"",
                    "q4": "Question 4: Overall, the mental demand to learn the video with this set of questions is",
                    "q5": "Question 5: Overall, the physical demand to learn the video with this set of questions is",
                    "q6": "Question 6: Overall, the learning satisfaction to learn the video with this set of "
                    "questions is",
                    "q7": "Question 7: Overall, I think this set of questions helps me recall facts and basic "
                    "concepts in this video.",
                    "q8": "Question 8: Overall, I think this set of questions helps me understand, explain concepts "
                    "and ideas in this video.",
                    "q9": "Question 9:  Overall, I think this set of questions helps me apply information in new "
                    "situations not in this video."}

# Setup connection with azure data table
connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

table_name = 'logs'
table_client = table_service_client.get_table_client(table_name=table_name)
entities = table_client.list_entities()

# Read current timestamps that are known to be valid participant data members
valid_members_file_path = 'valid_members.txt'
valid_members_file = open(valid_members_file_path, 'r')
valid_members_list = {}
for line in valid_members_file:
    temp = line.split()
    valid_members_list[temp[0]] = temp[1]
valid_members_file.close()
valid_members_file = open(valid_members_file_path, 'a')

# Read current timestamps that are known to be invalid participant data members
invalid_members_file_path = 'invalid_members.txt'
invalid_members_file = open(invalid_members_file_path, 'r')
invalid_members_list = []
for line in invalid_members_file:
    invalid_members_list.append(line.strip())
invalid_members_file.close()
invalid_members_file = open(invalid_members_file_path, 'a')

# Connect to Excel workbooks and prepares to overwrite current contents
answers_file_path = 'answers.xlsx'
answers_file = xlsxwriter.Workbook(answers_file_path)

chat_log_file_path = 'chat_logs.xlsx'
chat_log_file = xlsxwriter.Workbook(chat_log_file_path)

survey_file_path = 'surveys.xlsx'
survey_file = xlsxwriter.Workbook(survey_file_path)

qa_summary_file_path = 'qa_summaries.xlsx'
qa_summary_file = xlsxwriter.Workbook(qa_summary_file_path)


# Gets information about a field of one data member
def get_value(entity, field):
    if field == "timestamp":
        est_tz = timezone(timedelta(hours=-4), name="EST")
        return entity._metadata["timestamp"].astimezone(est_tz).isoformat()
    try:
        return entity[field]
    except KeyError:
        return None


# Writes a data member to the workbook
def write_to_workbook(data_member, participant):
    print("Participant " + participant + ": beginning data write")

    qa_summary = {"transcript": 0, "emotion": 0, "visual": 0}

    # Answers
    row = 0
    participant_worksheet = answers_file.add_worksheet(participant)
    for col, header in enumerate(answer_headers):
        participant_worksheet.write(row, col, header)
    row += 1
    answers = get_value(data_member, "answers")
    if answers is not None:
        try:
            decoded = json.loads(answers)
            prev_question = [-1, 1]
            for thing in decoded:
                question_data = thing["question"]
                if question_data["ID"] == prev_question[0]:
                    prev_question[1] += 1
                    row -= 1
                    participant_worksheet.write(row, 2, prev_question[1])
                    participant_worksheet.write(row, 3, "FALSE")
                else:
                    prev_question[0] = question_data["ID"]
                    prev_question[1] = 1
                    participant_worksheet.write(row, 0, question_data["question"])
                    participant_worksheet.write(row, 1, question_data["question_type"])
                    qa_summary[question_data["question_type"]] += 1
                    participant_worksheet.write(row, 2, 1)
                    participant_worksheet.write(row, 3, "TRUE")
                    participant_worksheet.write(row, 4, thing["time_to_answer"])
                    participant_worksheet.write(row, 5, question_data["time_stamp"])
                row += 1
            print("\tSuccessfully wrote answers")
        except (json.JSONDecodeError, TypeError):
            for col, header in enumerate(answer_headers):
                participant_worksheet.write(row, col, "Error reading data")
            print("\tError decoding answers")
    else:
        for col, header in enumerate(answer_headers):
            participant_worksheet.write(row, col, "No data")
        print("\tNo data for answers")

    # Chat log
    row = 0
    participant_worksheet = chat_log_file.add_worksheet(participant)
    for col, header in enumerate(chat_log_headers):
        participant_worksheet.write(row, col, header)
    row += 1
    chat_log = get_value(data_member, "chat_log")
    if chat_log is not None:
        try:
            decoded = json.loads(chat_log)
            for thing in decoded:
                participant_worksheet.write(row, 0, thing["prompt"])
                participant_worksheet.write(row, 1, thing["response"])
                row += 1
            print("\tSuccessfully wrote chat log")
        except (json.JSONDecodeError, TypeError):
            for col, header in enumerate(chat_log_headers):
                participant_worksheet.write(row, col, "Error reading data")
            print("\tError decoding chat log")
    else:
        for col, header in enumerate(chat_log_headers):
            participant_worksheet.write(row, col, "No data")
        print("\tNo data for chat log")

    # Survey
    row = 0
    participant_worksheet = survey_file.add_worksheet(participant)
    for col, header in enumerate(survey_headers):
        participant_worksheet.write(row, col, header)
    row += 1
    survey = get_value(data_member, "survey")
    if survey is not None:
        try:
            decoded = json.loads(survey)
            keys = decoded.keys()
            survey_info = []
            for index, key in enumerate(keys):
                temp1 = key.split('-')
                temp1.append(decoded[key])
                survey_info.append(temp1)
            for thing in survey_info:
                participant_worksheet.write(row, 0, survey_questions[thing[0]])
                participant_worksheet.write(row, 1, thing[1])
                participant_worksheet.write(row, 2, thing[2])
                row += 1
            print("\tSuccessfully wrote survey")
        except (json.JSONDecodeError, TypeError):
            for col, header in enumerate(survey_headers):
                participant_worksheet.write(row, col, "Error reading data")
            print("\tError decoding survey")
    else:
        for col, header in enumerate(survey_headers):
            participant_worksheet.write(row, col, "No data")
        print("\tNo data for survey")

    # QA Summary
    participant_worksheet = qa_summary_file.add_worksheet(participant)
    for col, header in enumerate(qa_summary_headers):
        participant_worksheet.write(0, col, header)
    error = True
    for value in qa_summary.values():
        if value != 0:
            error = False
    if not error:
        for col, value in enumerate(qa_summary.values()):
            participant_worksheet.write(1, col, value)
        print("\tSuccessfully wrote QA summary")
    else:
        for col in range(3):
            participant_worksheet.write(1, col, "No data")
        print("\tNo data for QA summary")

    # for col, key in enumerate(headers):
    #     value = get_value(entity, key)
    #     try:
    #         decoded_value = json.loads(value)
    #         worksheet.write(row, col, json.dumps(decoded_value))
    #     except (json.JSONDecodeError, TypeError):
    #         worksheet.write(row, col, value)


for entity_page in entities.by_page():
    # Allows the user to set new timestamps aside for review at the end
    unsure_members = []

    # Iterate through each data member stored in the database
    for entity in entity_page:
        # Check if the next data member loaded is recorded as a valid member (associated with a participant in study)
        # Or not (associated with a session done for fun, or testing, or just did not work, etc.)
        timestamp = get_value(entity, "timestamp")
        if timestamp in valid_members_list.keys():
            print("Timestamp " + timestamp + " is in valid_members - read with participant " +
                  valid_members_list[timestamp])
            write_to_workbook(entity, valid_members_list[timestamp])
        elif timestamp in invalid_members_list:
            print("Timestamp " + timestamp + " is in invalid_members - not read")
        else:
            valid_input = False

            while not valid_input:
                user_input = input("Timestamp " + timestamp + " is not recorded, is it valid " +
                                   "or not? (Can note unsure to come back at the end)\n  > ")

                if user_input.lower() in ["valid", "v", "1", "yes", "y"]:
                    user_input = input("Which participant is this timestamp associated with?\n > ")
                    if user_input.lower() not in ["quit", "cancel", "q", "c"]:
                        valid_members_file.write(timestamp + " " + user_input + "\n")
                        write_to_workbook(entity, user_input)
                        valid_input = True
                    else:
                        print("Canceled")
                elif user_input.lower() in ["unsure", "u", "2", "eh", "idk", "dunno"]:
                    unsure_members.append([timestamp, entity])
                    valid_input = True
                elif user_input.lower() in ["invalid", "i", "0", "no", "n"]:
                    invalid_members_file.write(timestamp + "\n")
                    valid_input = True
                else:
                    print("Invalid input, examples of valid responses include: valid, unsure, invalid, yes, idk, no")

    for timestamp, entity in unsure_members:
        valid_input = False

        while not valid_input:
            user_input = input("Timestamp " + timestamp + " is not recorded, is it valid or not? \n  > ")

            if user_input.lower() in ["valid", "v", "1", "yes", "y"]:
                user_input = input("Which participant is this timestamp associated with?\n > ")
                if user_input.lower() not in ["quit", "cancel", "q", "c"]:
                    valid_members_file.write(timestamp + " " + user_input + "\n")
                    write_to_workbook(entity, user_input)
                    valid_input = True
                else:
                    print("Canceled")
            elif user_input.lower() in ["invalid", "i", "0", "no", "n"]:
                invalid_members_file.write(timestamp + "\n")
                valid_input = True
            else:
                print("Invalid input, examples of valid responses include: valid, unsure, invalid, yes, idk, no")

answers_file.close()
chat_log_file.close()
survey_file.close()
qa_summary_file.close()

print(f"Answers saved to {answers_file_path}")
print(f"Chat logs saved to {chat_log_file_path}")
print(f"Surveys saved to {survey_file_path}")
print(f"QA summaries saved to {qa_summary_file_path}")
