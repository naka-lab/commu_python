package jp.nakalab;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ConcurrentLinkedQueue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import jp.vstone.RobotLib.CCommUMotion;
import jp.vstone.RobotLib.CPlayWave;
import jp.vstone.RobotLib.CRobotMem;
import jp.vstone.RobotLib.CRobotMotion;
import jp.vstone.RobotLib.CRobotPose;
import jp.vstone.RobotLib.CSotaMotion;
import jp.vstone.camera.CRoboCamera;
import jp.vstone.camera.FaceDetectLib.FaceUser;
import jp.vstone.camera.FaceDetectResult;
import jp.vstone.sotatalk.SpeechRecog;
import jp.vstone.sotatalk.SpeechRecog.RecogResult;
import jp.vstone.sotatalk.TextToSpeechSota;

// 音声合成スレッド
class SpeechSayThread extends Thread {
	ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<String>();
	boolean is_speaking = false;

	public void run() {
		while (true) {
			String content = this.queue.poll();
			if (content != null) {
				this.is_speaking = true;
				CPlayWave.PlayWave(TextToSpeechSota.getTTS(content), true);
			} else {
				this.is_speaking = false;

				try {
					Thread.sleep(100);
				} catch (Exception e) {
				}
			}

		}
	}

	public boolean is_speaking() {
		return this.is_speaking;
	}

	public void say(String content) {
		this.is_speaking = true;
		this.queue.add(content);
	}
}

class CommuStatus {
	public boolean is_speaking;
	public Short[] angles;
	public boolean is_moving;
}

class FaceInfo{
	public boolean is_detected = false;
	public boolean is_new_user = false;
	public int smile_score = -1;
	public int age = -1;
	public int sex = -1;
	public String name = "";
}

public class Test {
	public static void main(String[] args) {
		SpeechSayThread speech_say_thread = new SpeechSayThread();
		speech_say_thread.start();

		CRobotPose pose;
		CRobotMem mem = new CRobotMem();

		int timeout;
		RecogResult result;

		if (mem.Connect() == false) {
			System.out.println("commuとの接続失敗");
			return;
		}

		CRobotMotion motion = null;
		if (args.length == 0) {
			System.out.println("Argument to specify the robot type (sota or commu) is required. ");
			System.exit(-1);
		}

		String mode = args[0];
		if (mode.equals("commu")) {
			System.out.println("Initialize CommU");
			CCommUMotion motion_commu = new CCommUMotion(mem);
			motion_commu.InitRobot_CommU();
			motion = motion_commu;
		} else {
			System.out.println("Initialize Sota");
			CSotaMotion motion_sota = new CSotaMotion(mem);
			motion_sota.InitRobot_Sota();
			motion = motion_sota;
		}

		SpeechRecog recog = new SpeechRecog(motion);
		CRoboCamera cam = new CRoboCamera("/dev/video0", motion);

		ServerSocket sSocket = null;
		Socket socket = null;
		BufferedReader reader = null;
		PrintWriter writer = null;

		ObjectMapper mapper = new ObjectMapper();

		while (true) {
			try {
				sSocket = new ServerSocket(5000);

				while (true) {
					System.out.println("wait for client");
					socket = sSocket.accept();

					// 送受信用
					reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
					writer = new PrintWriter(socket.getOutputStream(), true);

					String line = null;
					FaceUser detected_user = null;

					while (true) {
						line = reader.readLine();
						System.out.println("recieved: " + line);

						if (line != null) {
							JsonNode node = mapper.readTree(line);
							String command = node.get("com").textValue();

							try {
								switch (command) {
								case "say":
									String content = node.get("content").textValue();
									speech_say_thread.say(content);
									writer.println("{\"result\": true}");
									break;
								case "servo_on":
									motion.ServoOn();
									writer.println("{\"result\": true}");
									break;
								case "servo_off":
									motion.ServoOff();
									writer.println("{\"result\": true}");
									break;
								case "set_pose":
									int size = node.get("angles").size();
									int time = node.get("time").intValue();
									Byte[] ids = new Byte[size];
									Short[] angles = new Short[size];
									for (int i = 0; i < size; i++) {
										ids[i] = (byte) node.get("ids").get(i).intValue();
										angles[i] = (short) node.get("angles").get(i).intValue();
									}
									pose = new CRobotPose();
									pose.SetPose(ids, angles);
									motion.play(pose, time);
									// motion.waitEndinterpAll();
									// 動きはじめるまで待機する
									while (motion.isEndInterpAll()) {
										Thread.sleep(10);
									}
									writer.println("{\"result\": true}");
									break;
								case "get_recog_res":
									timeout = node.get("timeout").intValue();
									result = recog.getRecognition(timeout);
									if (result != null && result.recognized) {
										String string = result.getBasicResult();
										System.out.println(string);
										writer.println(String.format("{\"result\": true, \"string\":\"%s\"}", string));
									} else {
										writer.println("{\"result\":false, \"string\":\"\"}");
									}
									break;
								case "get_yes_no":
									timeout = node.get("timeout").intValue();
									String yesno = recog.getYesorNo(timeout, 10);
									if (yesno == null) {
										writer.println("{\"result\":false, \"string\":\"\"}");
									} else if (yesno == "YES") {
										writer.println("{\"result\":true, \"string\": \"yes\"}");
									} else if (yesno == "NO") {
										writer.println("{\"result\":true, \"string\": \"no\"}");
									}
									break;
								case "get_recog_name":
									timeout = node.get("timeout").intValue();
									String name = recog.getName(timeout, 10);
									System.out.println(timeout);
									if (name != null) {
										writer.println(String.format("{\"result\": true, \"string\":\"%s\"}", name));
									} else {
										writer.println("{\"result\":false, \"string\":\"\"}");
									}
									break;
								case "start_face_track":
									cam.StartFaceTraking();
									writer.println("{\"result\": true}");
									break;
								case "stop_face_track":
									cam.StopFaceTraking();
									writer.println("{\"result\": true}");
									break;
								case "enable_face_estimation":
									boolean smile = node.get("face_smile").booleanValue();
									boolean search = node.get("face_search").booleanValue();
									boolean age_and_sex = node.get("age_and_sex").booleanValue();
									System.out.println(smile);
									System.out.println(search);
									System.out.println(age_and_sex);

									cam.setEnableSmileDetect(smile);
									cam.setEnableFaceSearch(search);
									cam.setEnableAgeSexDetect(age_and_sex);
									writer.println("{\"result\": true}");
									break;
								case "get_face_info":
									FaceDetectResult face_result = cam.getDetectResult();
									detected_user = cam.getUser(face_result);
									FaceInfo face_info = new FaceInfo();

									if(face_result.isDetect())
									{
										face_info.is_detected = true;
										face_info.smile_score = face_result.getSmile();
										face_info.is_new_user = detected_user.isNewUser();
										face_info.sex = detected_user.getSex();
										face_info.age = detected_user.getAge();
										if(!face_info.is_new_user){
											face_info.name = detected_user.getName();
										}
									}
									writer.println(mapper.writeValueAsString(face_info));
									break;
								case "add_user":
									String face_name = node.get("name").toString();
									int error_code = -1;
									if(detected_user != null ){
										detected_user.setName(face_name);
										System.out.println("***************");
										System.out.println(face_name);
										error_code = cam.addUserwithErrorCode(detected_user);

										if( error_code==1 ){
											writer.println( String.format( "{\"result\": true, \"code\":%d }", error_code));
											break;
										}
									}
									writer.println( String.format( "{\"result\": false, \"code\":%d }", error_code));
									break;
								case "remove_all_user":
									String[] all_user_names = cam.getAllUserNames();
									for(int i=0 ; i<all_user_names.length; i++){
										cam.removeUser(all_user_names[i]);
									}
									writer.println("{\"result\": true}");
									break;
								case "status":
									CommuStatus status = new CommuStatus();
									status.is_speaking = speech_say_thread.is_speaking();
									if (mode.equals("commu")) {
										status.angles = motion.getReadPose().getServoAngles(
												new Byte[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 });
									} else {
										status.angles = motion.getReadPose()
												.getServoAngles(new Byte[] { 1, 2, 3, 4, 5, 6, 7, 8 });
									}
									status.is_moving = !motion.isEndInterpAll();
									writer.println(mapper.writeValueAsString(status));
									break;
								default:
									System.out.println("未定義のコマンド："+command);
									break;


								}
							} catch (Exception e) {
								System.out.println("コマンド解析エラー");
								e.printStackTrace();
								writer.println("{\"result\": false}");
							}
						} else {
							break;
						}
					}

					// エラー起きたら再接続
					if (line == null) {
						break;
					}

				}
			} catch (Exception e) {
				e.printStackTrace();
			} finally {
				try {
					if (reader != null) {
						reader.close();
					}
					if (writer != null) {
						writer.close();
					}
					if (socket != null) {
						socket.close();
					}
					if (sSocket != null) {
						sSocket.close();
					}
					System.out.println("finished");
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}

}
