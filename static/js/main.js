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
                    console.log('=== COMPLETION DEBUG ===');
                    console.log('data.result exists:', !!data.result);
                    console.log('data.result:', data.result);
                    console.log('data.result.success:', data.result?.success);
                    console.log('data.result.clinic_count:', data.result?.clinic_count);
                    
                    if (data.result) {
                        if (data.result.success) {
                            console.log('✅ Showing result with success=true');
                            showResult(data.result);
                        } else {
                            console.log('❌ Result exists but success=false');
                            // フォールバック: progressからのclinic_countを使用
                            const fallbackResult = {
                                success: true,
                                clinic_count: data.clinic_count || 0,
                                filename: 'backup_result.csv',
                                download_url: '#',
                                error: data.result?.error
                            };
                            console.log('🔄 Using fallback result:', fallbackResult);
                            showResult(fallbackResult);
                        }
                    } else {
                        console.log('❌ No result object found - using fallback');
                        // フォールバック: progressからのデータで結果オブジェクトを構築
                        const fallbackResult = {
                            success: true,
                            clinic_count: data.clinic_count || 0,
                            filename: 'fallback_result.csv',
                            download_url: '#'
                        };
                        console.log('🔄 Using complete fallback result:', fallbackResult);
                        showResult(fallbackResult);
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
    
    console.log('=== SHOW RESULT DEBUG ===');
    console.log('result parameter:', result);
    console.log('result.clinic_count:', result.clinic_count);
    console.log('typeof result.clinic_count:', typeof result.clinic_count);
    
    // clinic_countが未定義または0の場合のデバッグ情報
    let clinicCount = result.clinic_count;
    
    // 厳密なタイプチェック
    if (clinicCount === undefined || clinicCount === null) {
        console.error('❌ CRITICAL: clinic_count is undefined/null!', result);
        clinicCount = 0;
    } else if (typeof clinicCount !== 'number') {
        console.error('❌ CRITICAL: clinic_count is not a number!', typeof clinicCount, clinicCount);
        clinicCount = parseInt(clinicCount) || 0;
    }
    
    // より詳細なデバッグ情報をページに表示
    const debugInfo = `デバッグ情報: clinic_count=${result.clinic_count} (${typeof result.clinic_count}) → 表示値=${clinicCount}`;
    console.log(debugInfo);
    
    // 0件の場合は警告メッセージも表示
    if (clinicCount === 0) {
        console.error('⚠️ WARNING: clinic_count is 0! Full result:', JSON.stringify(result, null, 2));
        resultMessage.innerHTML = `<strong>警告:</strong> ${clinicCount} 件の店舗情報を取得しました！<br><small class="text-muted">${debugInfo}</small><br><small class="text-warning">完全なレスポンス: ${JSON.stringify(result)}</small>`;
    } else {
        console.log(`✅ SUCCESS: Showing ${clinicCount} stores`);
        resultMessage.textContent = `${clinicCount} 件の店舗情報を取得しました！`;
    }
    
    // ダウンロードボタンの設定
    if (result.download_url && result.filename) {
        downloadBtn.href = result.download_url;
        downloadBtn.download = result.filename;
        downloadBtn.style.display = 'inline-block';
    } else {
        console.error('❌ Download URL or filename missing:', {
            download_url: result.download_url,
            filename: result.filename
        });
        downloadBtn.style.display = 'none';
    }
    
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