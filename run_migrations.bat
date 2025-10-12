@echo off
echo Activating conda environment...
call conda activate myenv
echo Running Django migrations...
python manage.py migrate
echo Migration process completed.
pause