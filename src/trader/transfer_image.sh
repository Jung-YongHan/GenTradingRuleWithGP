#!/bin/bash
echo "버전 설정을 진행합니다. 각 항목의 버전을 입력해주세요."

echo -n "[이미지명]: "
read -r service

# service="qrade-trader"
name="localhost:5000/$service"

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
echo  -n "설정하신 버전 확인? (Y/n) "
read -r isOk

if [ "$isOk" == "Y" ] || [ "$isOk" == "y" ]; then

  echo -n "[IP]: "
  read -r IP

#  echo -n "[PATH]: "
#  read -r PATH

  echo -n "[ID]: "
  read -r ID

  default_path="/home/$ID"

#  echo -n "[PW]: "
#  read -r PW
  image_path="/data/docker/images/$service$major$minor$patch.tar"

  echo $image_path
  sudo docker save -o $image_path $image_name
  sudo scp $image_path "$ID@$IP:/$default_path"
else
  echo "취소되었습니다."
fi

#echo  -n "설정하신 버전을 lastest 이미지로 만드시겠습니까? (Y/n) "
#read -r isOk
#if [ "$isOk" == "Y" ] || [ "$isOk" == "y" ]; then
#  echo "$image_name changed to $name:latest"
#  docker tag $image_name $name:latest
#
#  echo "push to docker hub - $name:latest"
#  docker push $name:latest
#else
#  echo "취소되었습니다."
#fi