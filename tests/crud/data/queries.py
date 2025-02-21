import datetime

query = """                                                                                                            
        CREATE TABLE test_table(                                                                                       
        id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,                                                               
        date date,                                                                                                     
        ticker varchar                                                                                                 
        );                                                                                                             
        """
insert_data = """                                                                                                      
        INSERT INTO test_table(                                                                                        
        date,                                                                                                          
        ticker                                                                                                         
        ) VALUES (%s,%s);                                                                                              
        """
data = ('2020-1-1', 'SBER')
read = """                                                                                                             
        SELECT * FROM {table};                                                                                      
        """
data_result = [(1, datetime.date(2020, 1, 1), 'SBER')]

read_days_off = """
        SELECT trade_date, ticker, closing_price, last_page
        FROM results_of_trades
        ORDER BY trade_date, ticker DESC ;
        """
dividends_lst = [
    ("2023-06-16", "MOEX", 4.84),
    ("2024-06-14", "MOEX", 17.35)

]
