import appconfig
import psycopg2
from flask import Flask, request, jsonify, render_template

print("Connecting to database...")
connection = psycopg2.connect(user=appconfig.db_user,
  password=appconfig.db_user_password,
  host=appconfig.db_host,
  port=appconfig.postgres_port,
  database="postgres_db",
  options="-c search_path=dbo,public")
  
cursor = conn.cursor()
