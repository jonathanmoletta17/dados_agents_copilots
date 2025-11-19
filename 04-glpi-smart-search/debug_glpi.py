import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from indexer.glpi_api import init_session, kill_session, search_tickets, _user_name, list_search_options

def debug():
    print("Initializing session...")
    token = init_session()
    if not token:
        print("Failed to init session")
        return

    try:
        print(f"Session token: {token[:5]}...")
        
        # 1. Check Search Options to verify field IDs
        print("\n--- Checking Search Options ---")
        opts = list_search_options(token, "Ticket")
        relevant = ["id", "name", "status", "users_id_recipient", "users_id_assign", "date_mod", "is_deleted"]
        field_ids = {}
        for o in opts:
            if o['field'] in relevant:
                print(f"Field '{o['field']}': ID {o['id']}")
                field_ids[o['field']] = o['id']
        
        # 2. Search for 1 ticket
        print("\n--- Searching for 1 ticket ---")
        tickets = search_tickets(token, include_deleted=False, range_len=1)
        if not tickets:
            print("No tickets found.")
        else:
            t = tickets[0]
            print("Ticket Data:", t)
            print(f"Requester (Raw): {t.get('REQUERENTE')}")
            print(f"Technician (Raw): {t.get('TECNICO')}")
            print(f"Mod Date: {t.get('DATA_MODIFICACAO')}")

        # 3. Test User Resolution explicitly
        print("\n--- Testing User Resolution ---")
        # Try to find a user ID from the ticket if possible, or just test a known ID if we had one.
        # We'll try to fetch the user for the requester of the ticket we found.
        # But wait, search_tickets already resolves it.
        # Let's look at the raw response of search_tickets to see what ID it *tried* to resolve.
        # We can't see the raw ID in the output of search_tickets because it replaces it.
        # I will modify this script to call the internal _do_query logic or just manually call the API.
        
        import urllib.request
        import json
        from indexer.glpi_api import _headers, _get_base_url
        
        base_url = _get_base_url()
        base = base_url.rstrip("/")+"/search/Ticket"
        
        # Manually construct query to see raw IDs
        qs = {
            "range": "0-1",
            "forcedisplay[0]": field_ids.get('users_id_recipient', 22), # Default 22
            "forcedisplay[1]": field_ids.get('users_id_assign', 5),     # Default 5
            "is_deleted": "0"
        }
        url = base + "?" + urllib.parse.urlencode(qs)
        print(f"Manual URL: {url}")
        req = urllib.request.Request(url, headers=_headers(token))
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("Raw API Response (First Item):")
            if data.get('data'):
                raw_row = data['data'][0]
                print(json.dumps(raw_row, indent=2))
                
                # Now try to resolve the user ID found
                recip_id = raw_row.get(str(field_ids.get('users_id_recipient', 22)))
                assign_id = raw_row.get(str(field_ids.get('users_id_assign', 5)))
                
                print(f"\nResolving Requester ID: {recip_id}")
                if recip_id:
                    print(f"Result: {_user_name(token, recip_id)}")
                
                print(f"Resolving Technician ID: {assign_id}")
                if assign_id:
                    print(f"Result: {_user_name(token, assign_id)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        kill_session(token)
        print("\nSession killed.")

if __name__ == "__main__":
    debug()
