import pandas as pd

folderpath = "F:\\Automation_of_HR_Work\\"
EmployeeData = pd.read_excel(f"{folderpath}Employee-Database.xlsx")
PayrollData = pd.read_excel(f"{folderpath}PayRollSummary.xlsx")

def calculate_tax(income):
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
    PayDataframe = pd.DataFrame()
    PayDataframe["DebitAccount"] = ["07020010095856760016"] * len(EmployeeData)
    PayDataframe[["PaidSalary", "Account Title", "Account #", "BANK"]] = EmployeeData[
        ["PaidSalary", "Account Title", "Account #", "BANK"]]

    AbFrame = PayDataframe.loc[PayDataframe["BANK"] == "ABPA"]
    PayDataframe = pd.concat([PayDataframe, AbFrame]).drop_duplicates(keep=False)

    return AbFrame,PayDataframe

def split_payments(PayDataframe,Salarylimit = 2.5*10**6):
    cf = []
    i = 0
    while len(PayDataframe) > 0:
        cf.append(PayDataframe[PayDataframe['PaidSalary'].cumsum() <= Salarylimit])
        PayDataframe = pd.concat([PayDataframe, cf[i]]).drop_duplicates(keep=False)
        i += 1
    return cf

def write_payments_to_txt(payments,AbFrame):
    for i, payment_df in enumerate(payments):
        payment_df.to_csv(f'Dispatch_{i}.txt', index=False, header=False)
        payment_df.loc[len(payment_df)] = "Total", str(payment_df['PaidSalary'].sum()), None, None, None
        payment_df.to_csv(f'{folderpath}Dispatch_{i}.csv', index=False, header=True)
    AbFrame.to_csv('Dispatch_AB.txt', index=False, header=False)
    AbFrame.loc[len(AbFrame)] = "Total", str(AbFrame['PaidSalary'].sum()), None, None, None
    AbFrame.to_csv(f'{folderpath}Dispatch_AB.csv', index=False, header=True)
        


EmployeeData = calculate_payroll(EmployeeData, PayrollData)
AbFrame,PayDataframe = prepare_payment_dataframe(EmployeeData)
payments = split_payments(PayDataframe)
write_payments_to_txt(payments,AbFrame)

