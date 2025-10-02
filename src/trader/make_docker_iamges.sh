#!/bin/bash
echo "버전을 설정을 진행합니다. 각 항목의 버전을 입력해주세요."
#name="rlwns012/qrade"
name="localhost:5000/qrade-trader"

image_name="$name"
echo -n "$image_name:    [메이저 버전]: "
read -r major

image_name="$name:$major"
echo -n "$image_name.  [마이너 버전]: "
read -r minor

image_name="$name:$major.$minor"
echo -n "$image_name.  [패치 버전]: "
read -r patch

image_name="$name:$major.$minor.$patch"
echo "최종 이미지:태그명 - $image_name"
echo  -n "설정하신 버전으로 이미지를 만드시겠습니까? (Y/n) "
read -r isOk

if [ "$isOk" == "Y" ] || [ "$isOk" == "y" ]; then
  pip list --format=freeze > requirements.txt

  sed -i '/TA-Lib/d' requirements.txt
  sed -i '/psycopg2/d' requirements.txt

  echo "$image_name image build start"
  docker build -t $image_name .

  echo "push to docker hub - $image_name"
  docker push $image_name
else
  echo "취소되었습니다."
fi

echo  -n "설정하신 버전을 lastest 이미지로 만드시겠습니까? (Y/n) "
read -r isOk
if [ "$isOk" == "Y" ] || [ "$isOk" == "y" ]; then
  echo "$image_name changed to $name:latest"
  docker tag $image_name $name:latest

  echo "push to docker hub - $name:latest"
  docker push $name:latest
else
  echo "취소되었습니다."
fi