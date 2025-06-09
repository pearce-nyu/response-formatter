import pandas as pd
import spacy as spacy
import re

# Load English model
nlp = spacy.load("en_core_web_sm")


##Helper method to clean up PreTest data
def PreTestCleanup(PreTestFile):
    PreTestA = pd.read_excel(PreTestFile)
    PreTestA = PreTestA.drop(0)
    PreTestA = PreTestA.drop(['Student Info. Form _1', 'Student Info. Form _3', 'Finished'], axis=1)
    PreTestA = PreTestA.rename(columns={
        'Student Info. Form _2': 'studentID', #Column names may change, adjust algorithm as needed
        'NA1_Q1: Pros': 'pre-q1-pro',
        'NA1_Q2: Cons': 'pre-q1-con',
        'NA2_Q1: Pros': 'pre-q2-pro',
        'NA2_Q2: Cons': 'pre-q2-con',
        'NA3_Q1: Pros': 'pre-q3-pro',
        'NA3_Q2: Cons': 'pre-q3-con',
        'Articles Clarity': 'pre-q4-articleclarity',
        'Questions Clarity': 'pre-q4-questionclarity'
    })
    PreTestA["studentID"] = PreTestA["studentID"].astype('int64')
    PreTestA
    return PreTestA

#Helper method to clean up postTest data
def PostTestCleanup(PostTestFile):
     #All information follows this format
    PostTestA = pd.read_excel(PostTestFile) #Converts the sheet into 
    PostTestA = PostTestA.drop(0) #Drops first row, which is extra info about columns
    PostTestA = PostTestA.drop(['Student Info. Form _1', 'Student Info. Form _3', 'Finished'], axis=1) #Drops Name, email, and finished
    PostTestA = PostTestA.rename(columns={
        'Student Info. Form _2': 'studentID', #Column names may change, adjust algorithm as needed
        'NA1_Q1: Pros': 'post-q1-pro',
        'NA1_Q2: Cons': 'post-q1-con',
        'NA2_Q1: Pros': 'post-q2-pro',
        'NA2_Q2: Cons': 'post-q2-con',
        'NA3_Q1: Pros': 'post-q3-pro',
        'NA3_Q2: Cons': 'post-q3-con',
        'Articles Clarity': 'post-q4-articleclarity',
        'Questions Clarity': 'post-q4-questionclarity'
    }) #Renames student ID column for clarity
    PostTestA["studentID"] = PostTestA["studentID"].astype('int64') #Converts student IDs from objects to int
    return PostTestA



#Sorts data into complete and incomplete
def merge(IdFile, PreTestAFile, PreTestBFile, PostTestAFile, PostTestBFile, OutputGroupACompleteFile,  OutputGroupBCompleteFile, OutputIncompleteFile):
    ids = pd.read_csv(IdFile) #Represents the original student ID and Participant ID data can change with read_excel if excel sheet
    ids = ids.rename(columns={'original-id': 'studentID'})
    ids = ids.drop(['note'], axis = 1) #drops notes, Pretest, and Posttest data

    PostTestA = PostTestCleanup(PostTestAFile)
    PostTestB = PostTestCleanup(PostTestBFile)

    PreTestA = PreTestCleanup(PreTestAFile)
    PreTestB = PreTestCleanup(PreTestBFile)

    ##dataPostTests = pd.merge(PostTestA, PostTestB, on='studentID', how = 'outer')
    dataPostTests = pd.merge(PostTestA, PostTestB, on='studentID', how = 'outer') ##Merges Posttest Data on StudentIDs
    dataPreTests = pd.merge(PreTestA, PreTestB, on='studentID', how = 'outer') ##Merges Pretest Data on StudentIDs
    dataTests = pd.merge(dataPostTests, dataPreTests, on='studentID', how = 'outer') #Merges all test data
    IdData = pd.merge(ids, dataTests, on='studentID', how = 'outer') #Merges test data with project IDs
    IdData = IdData.drop(["studentID"], axis = 1) #drops studentID
    print(IdData)
    
    #Column names may change, adjust algorithm as needed
    common_cols = ['Finished','pre-q1-pro', 'pre-q1-con','pre-q2-pro', 
                'pre-q1-pro', 'pre-q1-con','pre-q2-pro', 'pre-q2-con', 'pre-q3-pro',
                'pre-q3-con','pre-q4-articleclarity','pre-q4-questionclarity', 'post-q1-pro', 
                'post-q1-con', 'post-q2-pro',  'post-q2-con', 'post-q3-pro', 'post-q3-con', 
                'post-q4-articleclarity', 'post-q4-questionclarity']  # whatever overlaps
    

    for col in common_cols: #Combines from different tests (A or B) from pre-q1-pro_x and y columns into one column
        col_x = f"{col}_x"
        col_y = f"{col}_y"

        if col_x in IdData.columns and col_y in IdData.columns:
            IdData[col] = IdData[col_x].combine_first(IdData[col_y])
            IdData.drop([col_x, col_y], axis=1, inplace=True)
        elif col_x in IdData.columns:
            IdData.rename(columns={col_x: col}, inplace=True)
        elif col_y in IdData.columns:
            IdData.rename(columns={col_y: col}, inplace=True)

    
    complete_data = IdData.dropna() #Complete Data
    print(complete_data)
    incomplete_data = IdData[IdData.isnull().any(axis=1)] #Incomplete Data

    complete_data_GroupA = complete_data[complete_data["Pretest"] == 'A']
    print(complete_data_GroupA)
    complete_data_GroupB = complete_data[complete_data["Pretest"] == 'B']
    print(complete_data_GroupB)
    complete_data_GroupA.to_excel(OutputGroupACompleteFile, index=False)
    complete_data_GroupB.to_excel(OutputGroupBCompleteFile, index=False)
    incomplete_data.to_excel(OutputIncompleteFile, index=False)
    print("Output Files complete")

def tokenizer(inputFile, outputFile):
    data = pd.read_excel(inputFile)

    custom_order = [
        "pre-q1-pro", "pre-q1-con", "post-q1-pro", "post-q1-con", 
        "pre-q2-pro", "pre-q2-con", "post-q2-pro", "post-q2-con",
        "pre-q3-pro", "pre-q3-con", "post-q3-pro", "post-q3-con",
        "pre-q4-articleclarity", "pre-q4-questionclarity", 
        "post-q4-articleclarity", "post-q4-questionclarity"
    ]

    participant_col = "participant"
    tokenized_rows = []

    bullet_pattern = r"^(?:\d+\.\s+|•\s+|-\s+|-->\s+)"

    def process_question_set(question_set, data):
        for _, row in data.iterrows():
            participant_id = row[participant_col]
            
            for q in question_set:
                response = str(row.get(q, "")).strip()

                if response:
                    # Split response by line first (handles multi-line input with bullets)
                    lines = response.splitlines()

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # If it's a bullet/list line, treat the whole line as a sentence
                        if re.match(bullet_pattern, line):
                            tokenized_rows.append({
                                "participantID": participant_id,
                                "question": q,
                                "sentence": line
                            })
                        else:
                            # Let SpaCy split into sentences
                            doc = nlp(line)
                            for sent in doc.sents:
                                sent_text = sent.text.strip()
                                if sent_text:
                                    tokenized_rows.append({
                                        "participantID": participant_id,
                                        "question": q,
                                        "sentence": sent_text
                                    })

    for i in range(0, len(custom_order), 4):
        question_set = custom_order[i:i + 4]
        process_question_set(question_set, data)

    output_df = pd.DataFrame(tokenized_rows).dropna()
    output_df.to_excel(outputFile, index=False)
    print("✅ Tokenized data saved in output file")
    
def main(): ##Change all files as needed
    IdFile = "Ids_320h.csv" ##currently a csv but you can change the method to take in spreadsheets
    PreTestAFile =  "F24_320H_PreTestA.xlsx"   
    PreTestBFile = "F24_320H_PreTestB.xlsx"
    PostTestAFile = "F24_320H_PostTestA.xlsx"
    PostTestBFile = "F24_320H_PostTestB.xlsx"
    
    
    
    GroupACompleteData =  "Group_A_test_Complete_data.xlsx"      ##Output file with merged data for group A
    GroupBCompleteData =  "Group_B_test_Complete_data.xlsx"      ##Output file with merged data for group B
    IncompleteData = "test_Incomplete_data.xlsx"   ##Output File with incomplete data
    merge(IdFile, PreTestAFile, PreTestBFile, PostTestAFile, PostTestBFile, GroupACompleteData, GroupBCompleteData, IncompleteData) ##Merges all data
    GroupACompleteData_SentencesFile = "test_GroupA_Complete_Sentences.xlsx" ##Output file with tokenized data for group A
    GroupBCompleteData_SentencesFile = "test_GroupB_Complete_Sentences.xlsx" ##Output file with tokenized data for group B
    IncompleteData_SentencesFile = "test_Incomplete_Sentences.xlsx" ##Output file with tokenized data for incomplete sentences
    tokenizer(GroupACompleteData, GroupACompleteData_SentencesFile) ##Tokenizes Group A
    tokenizer(GroupBCompleteData, GroupBCompleteData_SentencesFile) ##Tokenizes Group B
    tokenizer(IncompleteData, IncompleteData_SentencesFile) ##Tokenizes incomplete data
    
    
if __name__ == '__main__':
    main()