from python:3.9

copy ./src/app.py /var/workdir/app.py
run pip install discord.py groq
workdir /var/workdir

cmd ["python" , "app.py"]