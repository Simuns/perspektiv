import sqlite3

# Open a connection to the database
conn = sqlite3.connect('artiklar.db')

# Create a cursor object to interact with the database
c = conn.cursor()

# Execute a SELECT statement
c.execute('SELECT id FROM artiklar WHERE fornavn = "Pimmi"')


# Fetch the results as a list of tuples
results = c.fetchall()


# Print the results
my_tuple = (results[0])

print(type(my_tuple))
text = ''.join(my_tuple)
print(text)
query = 'DELETE FROM artiklar WHERE yvirskrift = ""'

def delete(query):

    c.execute(query)
    conn.commit()

    print(f"{c.rowcount} rows deleted.")
delete(query)
# Close the cursor and connection
c.close()
conn.close()


def preview_text(text, preview_lenght=50):
    import re

    ###THIS SECTION REMOVES ALL HTML SYNTAX FROM TEXT###
    # Define the regular expression pattern to search for
    pattern = r"<[^>]+>"

    # Define the replacement string
    replacement = ''

    # Replace all occurrences of the pattern in the text with the replacement string
    clean_text = re.sub(pattern, replacement, text)

    ### THIS SECTION CUTS THE TEXT TO PREVIEW ###
    words = clean_text.split()
    if len(words) < preview_lenght:
        print(f"The string has less than {preview_lenght} words.")
        return clean_text
    else:
        shortened_text = " ".join(words[:preview_lenght])
        return shortened_text
