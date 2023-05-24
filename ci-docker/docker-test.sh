#!/bin/bash
mkdir -p logs
docker-compose -f docker-compose.test.yml up -d
sleep 60

docker ps -a
ID=$(docker container ls -qf "name=tests")

while ! docker logs --tail 1 "$ID" | grep 'TESTS READY'
do
    printf "\n"
    echo "Waiting for tests to complete, please be patient. Status:"
    docker-compose -f docker-compose.test.yml logs --tail=2 b2share-test
    sleep 60
done

echo "Tests has completed"

docker logs -t tests > ../logs.log

docker cp "$ID":/eudat/b2share/coverage.xml ../coverage.xml
docker cp "$ID":/eudat/b2share/junit.xml ../junit.xml

docker-compose -f docker-compose.test.yml down

cat ../logs.log

if grep -q "[1-9]\d* failed" ../logs.log || grep -q "[1-9]\d* error" ../logs.log
then
    echo "We have fails or errors!"
    grep "[1-9]\d* failed" ../logs.log
    grep "[1-9]\d* error" ../logs.log
    exit 1
elif grep -q "[1-9]\d* xfailed" ../logs.log
then
    echo "We have accepted fails (xfailed)!"
    grep "[1-9]\d* xfailed" ../logs.log
    exit 22
elif grep -q "[1-9]\d* passed" ../logs.log
then
    echo "No failures!"
else
    echo "ERROR"
    exit 1
fi
