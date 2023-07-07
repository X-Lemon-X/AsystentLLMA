import Asistant as asis
import FaceRecognition as fr
import FaceLibLLMWraper as flw
import CommandLineWraper as clw


#face = fr.FacesLib()
#faceWraper = flw.FaceCodesWraper(faceRecogninito=face, commands_file="/home/lemonx/IT/projects/asystent/lib/face_llm_wraper.json")
#face.LoadFaces()
#face.StartCapture()
cli = clw.CommandLine()



asystant = asis.Assistant(6)
#asystant.add_new_extenssion(commands_file="/home/lemonx/IT/projects/asystent/face_llm_wraper.json", handler_to_call_for_given_command=faceWraper.HandleCommand, class_reference=faceWraper)
asystant.add_new_extenssion(commands_file="/home/lemonx/IT/projects/asystent/commandLine_llm_wraper.json", handler_to_call_for_given_command=cli.HandleCommand, class_reference=cli)


#asystant.handle_multi_command("You want to exit Google Photos. To do this you can use the following command: \n```G1```\nNote that no argument is needed for this command.")

asystant.run_assistant()

asystant.__del__()

