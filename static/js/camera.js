function takePhoto(deviceId) {
    console.log('takePhoto function called with deviceId:', deviceId);
    const video = document.createElement('video');
    video.style.display = 'none';
    document.body.appendChild(video);

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        .then(function (stream) {
            console.log('Camera access granted');
            video.srcObject = stream;
            video.setAttribute('playsinline', true);
            video.play();

            // 0.5秒後に撮影
            setTimeout(function () {
                console.log('Taking photo...');
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                // Base64形式で画像データを取得
                const imageData = canvas.toDataURL('image/png');
                console.log('Image data captured, size:', imageData.length);

                // 画像データをサーバーに送信
                uploadInnerPhoto(deviceId, imageData);

                // ストリームを停止
                stream.getTracks().forEach(track => track.stop());
                video.remove();
                canvas.remove();
                console.log('Camera resources cleaned up');
            }, 500);
        })
        .catch(function (error) {
            console.error('Error accessing inner camera:', error);
            alert('内カメラへのアクセスに失敗しました: ' + error);
            video.remove();
        });
}

function uploadInnerPhoto(deviceId, imageData) {
    console.log('uploadInnerPhoto called with deviceId:', deviceId);
    fetch('/upload_inner_photo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: deviceId, image: imageData })
    })
    .then(response => {
        console.log('Server response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Server response data:', data);
        if (data.status === 'success') {
            console.log('Inner photo uploaded successfully:', data.path);
        } else {
            console.error('Failed to upload inner photo:', data.message);
        }
    })
    .catch(error => {
        console.error('Error uploading inner photo:', error);
    });
}
