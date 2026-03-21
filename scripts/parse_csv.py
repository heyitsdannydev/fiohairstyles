import csv
import datetime
import os

def parse_date(date_str: str, year: str = "2026") -> str:
    """Parse date string in format 'd/m' or 'month_name' to ISO datetime format."""
    if not date_str or date_str.strip() == "":
        return ""
    
    date_str = date_str.strip().lower()
    
    # Month mapping
    months = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, 
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    
    # Try parsing as month name
    if date_str in months:
        month = months[date_str]
        dt = datetime.datetime(int(year), month, 1, 0, 0, 0)
        return dt.isoformat()
    
    # Try parsing as d/m format
    if "/" in date_str:
        try:
            parts = date_str.split("/")
            day = int(parts[0])
            month = int(parts[1])
            dt = datetime.datetime(int(year), month, day, 0, 0, 0)
            return dt.isoformat()
        except:
            return ""
    
    return ""


def parse_csv():
    """Parse clients.csv and create clients_parsed.csv."""
    input_file = os.path.join(os.path.dirname(__file__), "clients.csv")
    output_file = os.path.join(os.path.dirname(__file__), "clients_parsed.csv")
    
    try:
        # Read input CSV
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Get all fieldnames and remove the first column (2026)
            fieldnames = [col for col in reader.fieldnames if col != "2026"]
            
            # Write output CSV
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                row_count = 0
                for row in reader:
                    # Skip empty rows or header rows
                    if not row.get("Client", "").strip():
                        continue
                    
                    # Parse dates
                    service_datetime = parse_date(row.get("ServiceDateTime", ""))
                    down_payment_date = parse_date(row.get("DownPaymentDate", ""))
                    remaining_payment_date = parse_date(row.get("RemainingPaymentDate", ""))
                    
                    # Create new row with parsed dates
                    new_row = {}
                    for field in fieldnames:
                        if field == "ServiceDateTime":
                            new_row[field] = service_datetime
                        elif field == "DownPaymentDate":
                            new_row[field] = down_payment_date
                        elif field == "RemainingPaymentDate":
                            new_row[field] = remaining_payment_date
                        else:
                            new_row[field] = row.get(field, "")
                    
                    writer.writerow(new_row)
                    row_count += 1
                    
                    if row.get("Client"):
                        print(f"✓ Parsed: {row.get('Client')} - {service_datetime}")
        
        print(f"\n✅ Successfully parsed {row_count} rows!")
        print(f"Output saved to: {output_file}")
    
    except FileNotFoundError:
        print(f"❌ Error: clients.csv file not found at {input_file}")
    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")


if __name__ == "__main__":
    parse_csv()
