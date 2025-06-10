# PEaRCE Project - Sentence Tokenezation Algorithm

This algorithm takes in the pretest and posttest spreadsheets for each group, along with a spreadsheet or csv data containing the student id and cooresponding anonoimized id. It then converts it into

1. Three spreadsheets of merged data. For Group A, Group B, and incomplete data respectively AND

2. Three spreadsheets of tokenized data, cooresponding to Group A, Group B, and incomplete data respectively.

Input data of the tests should include following column names (which are the default names of the questions in the Qualtrics survey)

1. Finished
2. Student Info. Form _1
3. Student Info. Form _2
4. Student Info. Form _3
5. NA1_Q1: Pros
6. NA1_Q2: Cons
7. NA2_Q1: Pros
8. NA2_Q2: Cons
9. NA3_Q1: Pros
10. NA3_Q2: Cons
11. Articles Clarity
12. Questions Clarity

Input data for the anonimized id should include the following columns (participant represents anonimized ids)
1. original-id,
2. participant

To use the algorithm modify variables in the main method
1. Each of the first five variables (IdFile, PreTestAFile, PreTestBFile, PostTestAFile, and PostTestBFile) must take in string with the name representation of the cooresponding input file (ex: "F24_320H_PreTestA.xlsx"). The IdFile currently takes in csv files, but you can modify it to take in spreadsheets in the cooresponding part of the merge algorithm.
2. Each of the next three variables (GroupACompleteData, GroupBCompleteData, and IncompleteData) represent the output files of the merged data. Change the string to represent the desired output file name.
3. The final three variables (GroupACompleteData_SentencesFinal, GroupBCompleteData_SentencesFile, and IncompleteData_SentencesFile) represent the output files of the tokenized data. Change the string to represent the desired output file name.

Running the code will then produce each of the six output files with the cooresponding output file names. 

Note: The code considers each list item as a separate sentence.

Note: There might be errors or redundancies in the output, which should be cleaned manually.
