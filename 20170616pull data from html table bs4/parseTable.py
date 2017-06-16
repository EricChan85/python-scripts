
from bs4 import BeautifulSoup
from mysqlDB import *

html_name = "TradingInfo.html"

def text_or_null(text):
    text = text.strip()
    return text if text != "" else "NULL"

def parse_tr(tr):
    two_line = True
    record = ""
    comment = ""
    idx = 0    
    for td in tr.find_all("td"):
        idx += 1
        if td.has_attr("colspan"):
            colspan = (int)(td["colspan"])            
            if idx == 1 and colspan > 9:
                return "", tr, True
            idx += (colspan - 1)
            for i in range(colspan):
                record += ",NULL"
            comment = td.get_text()
            two_line = False
        else:            
            if idx == 1:
                record = td.get_text().strip()
            elif idx == 2 or idx == 3 or idx == 5 or idx == 9:
                text = td.get_text().strip()
                record += ",\"" + text_or_null(td.get_text()) + "\""
            elif idx == 14:                
                record += "," + text_or_null(td.get_text()).replace(" ", "")
            else:
                record += "," + text_or_null(td.get_text())
    if two_line:
        tr = tr.find_next_sibling("tr")
        td = tr.find("td")
        td = td.find_next_sibling("td")
        record += "," + text_or_null(td.get_text())
        td = td.find_next_sibling("td")
        record += ",\"" + td.get_text() + "\""
    else:
        record += ",NULL,\"" + comment + "\""
    return record, tr, False
    
    
def main():
    print ("start")
    with open(html_name) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    record = ""
    current_is_end = False
    sql = "INSERT INTO record VALUES "
    tr = soup.find("tr", bgcolor="#C0C0C0")
    count = 0
    while not current_is_end:        
        tr = tr.find_next_sibling("tr")
        record, tr, current_is_end = parse_tr(tr)
        if record != "":
            if count == 0:
                sql += "(" + record + ")"
            else:
                sql += ",(" + record + ")"
        count += 1
 
    print (sql)
    conn = connect()
    insert(conn, sql)
    close_connection(conn)
if __name__ == "__main__":
    main()
