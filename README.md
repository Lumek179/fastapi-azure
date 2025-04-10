To Start the Local Testing
docker compose -f docker-compose.yml up -d

To Test the creation of records:
http://localhost:8000/seed POST

To Get the Records of a db via API
http://localhost:8000/items GET