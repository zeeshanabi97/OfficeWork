import pandas as pd
def calculate_tax(income:float):
    
    """
Calculate tax based on income brackets.

Args:
income (float): The income amount to calculate tax for.

Returns:
float: The calculated tax amount based on the provided income.

Calculates tax based on income brackets:
- Over 6,000,000: 35% tax on the amount exceeding 6,000,000 plus 1,095,000
- Over 3,600,000: 27.5% tax on the amount exceeding 3,600,000 plus 435,000
- Over 2,400,000: 22.5% tax on the amount exceeding 2,400,000 plus 165,000
- Over 1,200,000: 12.5% tax on the amount exceeding 1,200,000 plus 15,000
- Over 600,000: 2.5% tax on the amount exceeding 600,000
- Up to 600,000: No tax
    """
    if income > 6000000:
        return (income - 6000000) * 0.35 + 1095000
    elif income > 3600000:
        return (income - 3600000) * 0.275 + 435000
    elif income > 2400000:
        return (income - 2400000) * 0.225 + 165000
    elif income > 1200000:
        return (income - 1200000) * 0.125 + 15000
    elif income > 600000:
        return (income - 600000) * 0.025
    elif income > 0:
        return 0
    else:
        return 0

def calculate_payroll(EmployeeData, PayrollData):
    
    """
Calculate payroll details for employees.

Args:
EmployeeData (pandas.DataFrame): DataFrame containing employee information.
PayrollData (pandas.DataFrame): DataFrame containing payroll information.

Returns:
pandas.DataFrame: DataFrame with calculated payroll details for each employee.

This function computes the payroll for employees by merging the provided
EmployeeData and PayrollData DataFrames. It extracts necessary columns
like EmployeeID, MonthlyIncome, and First Name, calculates AnnualIncome,
and returns a DataFrame with payroll details for each employee.
"""
    Payroll = pd.DataFrame()
    Payroll[['EmployeeID', 'MonthlyIncome']] = PayrollData[["Employee ID", "Monthly Salary"]]
    Payroll = pd.merge(Payroll, EmployeeData[["EmployeeID", "First Name"]], on='EmployeeID', how='inner')
    Payroll["AnnualIncome"] = Payroll["MonthlyIncome"] * 12

    tax = [calculate_tax(x) for x in Payroll["AnnualIncome"]]
    Payroll["AnnualTax"] = tax
    Payroll["MonthlyTax"] = Payroll["AnnualTax"] / 12
    Payroll["PaidSalary"] = Payroll["MonthlyIncome"] - Payroll["MonthlyTax"]
    Payroll.to_csv('payroll_data.csv', index=False)

    EmployeeData = pd.merge(EmployeeData, Payroll[["EmployeeID", "PaidSalary"]], on='EmployeeID', how='inner')
    return EmployeeData

def prepare_payment_dataframe(EmployeeData):
    
    """
   Prepare payment DataFrame for employee salaries.

   Args:
   EmployeeData (pandas.DataFrame): DataFrame containing employee payment information.

   Returns:
   tuple: A tuple containing two DataFrames:
          - AbFrame: DataFrame with payment details for a specific bank (ABPA)
          - PayDataframe: DataFrame with payment details for other banks

   This function prepares a payment DataFrame for employee salaries by creating
   'DebitAccount' column with a default value, extracting relevant columns such as
   'PaidSalary', 'Account Title', 'Account #', and 'BANK' from the provided EmployeeData.
   It separates the payment details for a specific bank (ABPA) into AbFrame and
   other banks' payment details into PayDataframe. Both DataFrames are then returned
   as a tuple.
   """
    
    PayDataframe = pd.DataFrame()
    PayDataframe["DebitAccount"] = ["07020010095856760016"] * len(EmployeeData)
    PayDataframe[["PaidSalary", "Account Title", "Account #", "BANK"]] = EmployeeData[
        ["PaidSalary", "Account Title", "Account #", "BANK"]]

    AbFrame = PayDataframe.loc[PayDataframe["BANK"] == "ABPA"]
    PayDataframe = pd.concat([PayDataframe, AbFrame]).drop_duplicates(keep=False)

    return AbFrame,PayDataframe

def split_payments(PayDataframe,Salarylimit = 2.5*10**6):
    """
    Split payments from a DataFrame based on a salary limit.

    Args:
    PayDataframe (pandas.DataFrame): DataFrame containing payment information.
    Salarylimit (float): The maximum salary limit for each payment group. Default is 2.5 million.

    Returns:
    list: A list containing DataFrames representing split payments.

    This function divides payments from the provided PayDataframe into multiple DataFrames
    based on a salary limit. It accumulates payments until the cumulative paid salary
    reaches the defined Salarylimit, then creates a new DataFrame with those payments.
    It continues this process until all payments are distributed into separate DataFrames
    based on the specified salary limit, returning a list of these divided DataFrames.
    """
    cf = []
    i = 0
    while len(PayDataframe) > 0:
        cf.append(PayDataframe[PayDataframe['PaidSalary'].cumsum() <= Salarylimit])
        PayDataframe = pd.concat([PayDataframe, cf[i]]).drop_duplicates(keep=False)
        i += 1
    return cf

def write_payments_to_txt(payments,AbFrame):
    """
Write payment details to text and CSV files.

Args:
payments (list): List of DataFrames representing different payment groups.
AbFrame (pandas.DataFrame): DataFrame containing payment details for a specific bank.

This function writes payment details from the provided 'payments' list and AbFrame
DataFrame to separate text and CSV files. It iterates through each DataFrame in 'payments',
writes the payment details to both text and CSV files, appends a total payment summary at
the end of each file, and writes payment details from AbFrame to separate text and CSV files
with the total payment summary appended.
"""
    
    for i, payment_df in enumerate(payments):
        payment_df.to_csv(f'Dispatch_{i}.txt', index=False, header=False)
        payment_df.loc[len(payment_df)] = "Total", str(payment_df['PaidSalary'].sum()), None, None, None
        payment_df.to_csv(f'{folderpath}Dispatch_{i}.csv', index=False, header=True)
    AbFrame.to_csv('Dispatch_AB.txt', index=False, header=False)
    AbFrame.loc[len(AbFrame)] = "Total", str(AbFrame['PaidSalary'].sum()), None, None, None
    AbFrame.to_csv(f'{folderpath}Dispatch_AB.csv', index=False, header=True)
        
def main():
    folderpath = "F:\\Automation_of_HR_Work\\"
    EmployeeData = pd.read_excel(f"{folderpath}Employee-Database.xlsx")
    PayrollData = pd.read_excel(f"{folderpath}PayRollSummary.xlsx")

    EmployeeData = calculate_payroll(EmployeeData, PayrollData)
    AbFrame,PayDataframe = prepare_payment_dataframe(EmployeeData)
    payments = split_payments(PayDataframe)
    write_payments_to_txt(payments,AbFrame)
if __name__ == "__main__":
    main()
