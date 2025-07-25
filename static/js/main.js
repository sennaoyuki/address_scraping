// クリニック店舗情報スクレイパー メインスクリプト

let currentSessionId = null;
let progressInterval = null;

// フォーム送信処理
document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = document.getElementById('urlInput').value;
    const submitBtn = document.getElementById('submitBtn');
    
    // UIをリセット
    resetUI();
    
    // ボタンを無効化
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>処理中...';
    
    try {
        // スクレイピングを開始
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            showProgressArea();
            startProgressTracking();
        } else {
            showError(data.error || '処理を開始できませんでした。');
        }
    } catch (error) {
        showError('サーバーとの通信に失敗しました。');
    } finally {
        // ボタンを有効化
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-cloud-download"></i> スクレイピング開始';
    }
});

// 進捗状況を追跡
function startProgressTracking() {
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/progress/${currentSessionId}`);
            const data = await response.json();
            
            console.log('Progress data:', data); // デバッグ用
            
            if (response.ok) {
                updateProgress(data);
                
                if (data.completed) {
                    clearInterval(progressInterval);
                    if (data.result && data.result.success) {
                        console.log('Result:', data.result); // デバッグ用
                        showResult(data.result);
                    } else {
                        showError(data.result?.error || '処理中にエラーが発生しました。');
                    }
                }
            } else {
                clearInterval(progressInterval);
                showError('進捗情報の取得に失敗しました。');
            }
        } catch (error) {
            clearInterval(progressInterval);
            showError('サーバーとの通信に失敗しました。');
        }
    }, 1000); // 1秒ごとに更新
}

// 進捗状況を更新
function updateProgress(data) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const statusMessage = document.getElementById('statusMessage');
    const actionText = document.getElementById('actionText');
    
    const percentage = data.percentage || 0;
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
    
    statusMessage.textContent = data.status || '処理中...';
    actionText.textContent = data.current_action || '';
}

// 結果を表示
function showResult(result) {
    const resultArea = document.getElementById('resultArea');
    const resultMessage = document.getElementById('resultMessage');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // clinic_countが未定義または0の場合のデバッグ情報
    const clinicCount = result.clinic_count || 0;
    console.log('Showing result with clinic_count:', clinicCount, 'from result:', result);
    
    // より詳細なデバッグ情報をページに表示
    const debugInfo = `デバッグ情報: clinic_count=${result.clinic_count}, typeof=${typeof result.clinic_count}`;
    console.log(debugInfo);
    
    // 0件の場合は警告メッセージも表示
    if (clinicCount === 0) {
        console.error('WARNING: clinic_count is 0!', result);
        resultMessage.innerHTML = `<strong>警告:</strong> ${clinicCount} 件の店舗情報を取得しました！<br><small class="text-muted">${debugInfo}</small>`;
    } else {
        resultMessage.textContent = `${clinicCount} 件の店舗情報を取得しました！`;
    }
    
    downloadBtn.href = result.download_url;
    downloadBtn.download = result.filename;
    
    hideProgressArea();
    resultArea.style.display = 'block';
    
    // 古いファイルをクリーンアップ
    cleanupOldFiles();
}

// エラーを表示
function showError(message) {
    const errorArea = document.getElementById('errorArea');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    
    hideProgressArea();
    errorArea.style.display = 'block';
}

// 進捗エリアを表示
function showProgressArea() {
    document.getElementById('progressArea').style.display = 'block';
}

// 進捗エリアを非表示
function hideProgressArea() {
    document.getElementById('progressArea').style.display = 'none';
}

// UIをリセット
function resetUI() {
    document.getElementById('progressArea').style.display = 'none';
    document.getElementById('resultArea').style.display = 'none';
    document.getElementById('errorArea').style.display = 'none';
    
    // 進捗バーをリセット
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    
    // インターバルをクリア
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// 古いファイルをクリーンアップ
async function cleanupOldFiles() {
    try {
        await fetch('/api/cleanup', {
            method: 'POST'
        });
    } catch (error) {
        console.error('クリーンアップエラー:', error);
    }
}

// URLの例を自動入力
document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const examples = [
        'https://dioclinic.jp/clinic/',
        'https://eminal-clinic.jp/clinic/',
        'https://www.rizeclinic.com/locations/',
        'https://frey-a.jp/clinic/',
        'https://drskinclinic.jp/clinic/',
        'https://lietoclinic.com/clinic/',
        'https://beautyskinclinic.jp/clinic/',
        'https://www.mens-life-clinic.com/clinic/'
    ];
    
    // プレースホルダーをランダムに変更
    const randomExample = examples[Math.floor(Math.random() * examples.length)];
    urlInput.placeholder = randomExample;
});