
#  Check for custom caption in custom_cap.txt
with open(os.getcwd + '/' + self.me + '/' + 'custom_cap.txt') as custom_cap:
    cap = custom_cap.read().splitlines()
