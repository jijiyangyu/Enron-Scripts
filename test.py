import os

def Test(rootDir): 
    list_dirs = os.walk(rootDir)
    email = {}
    email["content"] = ""
    tag_end = False
    for root, dirs, files in list_dirs:     
        for f in files: 
            if f[-3:].upper()=='TXT':
                email_file = open(f)
                print os.path.split(root)[1], f
                for line in email_file:
                    if tag_end==True:
                       field = "content" 
                       email[field] = email[field] + "\n" + line
                    else:
                       field = line.split(":")[0]
                       value = line[len(field) + 2 :]
                       field = field.strip()
                       value = value.strip()
                       email[field] = value
                       if field=="To":
                           email[field] = value.split(",")
                       elif field=="X-FileName":
                           tag_end = True
                    print field, email[field]
			
Test("/Users/Xiang/Desktop/Python/Enron")
