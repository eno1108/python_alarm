from datetime import datetime, timedelta
import os
import subprocess
import sys
import time

# 再生したい MP3 / WAV などの音声ファイルのフルパス
AUDIO_FILE = r"F:\music\ずんだダンシング.mp3"


def send_windows_notification(title: str, message: str) -> None:
    """Windows標準のトースト通知を表示"""
    ps_cmd = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textNodes = $template.GetElementsByTagName("text")
    $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
    $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Python Alarm")
    $notification = [Windows.UI.Notifications.ToastNotification]::new($template)
    $notifier.Show($notification)
    """
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)


def play_mp3(file_path: str) -> None:
    """Windows標準のMediaPlayerを使用してバックグラウンドでMP3を再生"""
    if not os.path.exists(file_path):
        print(f"\n[警告] 音声ファイル '{file_path}' が見つかりません。")
        return

    # PowerShellのMediaPlayer機能を利用
    ps_audio_cmd = f"""
    Add-Type -AssemblyName presentationCore
    $mediaPlayer = New-Object system.windows.media.mediaplayer
    $mediaPlayer.open('{file_path}')
    $mediaPlayer.Play()
    Start-Sleep 1
    # ユーザーが Enter を押すまで再生（最大300秒）
    for ($i = 0; $i -lt 300; $i++) {{
        Start-Sleep 1
    }}
    """
    # 非同期で音声を再生開始
    proc = subprocess.Popen(["powershell", "-Command", ps_audio_cmd])

    print("\n⏰ アラーム鳴動中！ [Enter] キーを押すと停止します...")
    try:
        input()
    finally:
        # Enterが押されたら停止
        proc.terminate()


def main():
    while True:
        raw_input = input("アラーム時刻を入力してください (HH:MM): ").strip()
        try:
            alarm_time = datetime.strptime(raw_input, "%H:%M").time()
            break
        except ValueError:
            print("時刻は HH:MM 形式で入力してください。")

    now = datetime.now()
    alarm = datetime.combine(now.date(), alarm_time)
    if alarm <= now:
        alarm += timedelta(days=1)

    print(f"\n{alarm:%Y-%m-%d %H:%M} にアラームを設定しました。(Ctrl+C で中断)\n")

    try:
        while True:
            remaining = (alarm - datetime.now()).total_seconds()
            if remaining <= 0:
                break

            mins, secs = divmod(int(remaining), 60)
            hours, mins = divmod(mins, 60)
            sys.stdout.write(f"\r残り時間: {hours:02d}:{mins:02d}:{secs:02d} ")
            sys.stdout.flush()

            time.sleep(min(1.0, max(0.1, remaining)))

    except KeyboardInterrupt:
        print("\n\nアラームをキャンセルしました。")
        return

    # 通知とMP3再生
    send_windows_notification("⏰ アラーム", f"{alarm:%H:%M} になりました！")
    play_mp3(AUDIO_FILE)


if __name__ == "__main__":
    main()
