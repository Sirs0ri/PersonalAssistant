import glob, re

files = glob.glob("{}/*".format("C:\\Users\\ertlm\\Desktop\\Logs"))

print()
print("Found {} files.".format(len(files)))
print()

matchcount = 0
filecount = 0
noOfFiles = len(files)
matches = []
pattern = (r"(?P<date>[\d-]+) "
           r"(?P<time>[\d:,]+) "
           r"(?P<level>[a-zA-Z]+)\s*(?P<plugin>[a-zA-Z\.]+\s*) "
           r"(?P<message>[\S ]*)")
errors = {}

def parse(s):
    global matchcount
    matchcount += 1
    m = re.match(pattern, s)
    d = m.groupdict()
    hour = int(d["time"].split(":")[0])
    msg = d["message"]
    if not msg in errors:
        errors[msg] = {"count": 0, "times": {hour: 0 for hour in range(24)}}
    errors[msg]["count"] += 1
    errors[msg]["times"][hour] += 1
    # 2017-01-24 13:21:37,902 WARNING  samantha.plugins.weather
    # The request returned the wrong status code: 500
    
    
for file in files:
    with open(file) as f:
        linecount = 0
        filecount += 1
        lines = f.readlines()
        noOfLines = len(lines)
        for line in lines:
            linecount += 1
            print("\rProcessing File {} of {}.\t{}{}\t Matches so far: {}"
                  .format(filecount,
                          noOfFiles,
                          "#"*int(20*linecount/noOfLines),
                          "-"*(20-int(20*linecount/noOfLines)),
                          matchcount), end="")
            if "samantha.plugins.weather The request returned the wrong status code:" in line:
                parse(line)
                

print()
print("Found {} matches in {} lines.".format(matchcount, linecount))
print()

times_all = {hour: 0 for hour in range(24)}
for e in errors:
    count = errors[e]["count"]
    times = errors[e]["times"]
    print("\"{}\"\toccurred {} times.".format(e, count))
    print("This error occurred at: -------------------------")
    for hour in times:
        times_all[hour] += times[hour]
        print("%02d.00-%02d.59    %5d    %s%s" % (
            hour,
            hour,
            times[hour],
            "#"*int(25*times[hour]/count),
            "-"*(25-int(25*times[hour]/count))))
    print()
    

count = errors[e]["count"]
times = errors[e]["times"]

print("All errors occurred at: -------------------------")
for hour in times_all:
    print("%02d.00-%02d.59    %5d    %s%s" % (
        hour,
        hour,
        times_all[hour],
        "#"*int(25*times_all[hour]/matchcount),
        "-"*(25-int(25*times_all[hour]/matchcount))))
