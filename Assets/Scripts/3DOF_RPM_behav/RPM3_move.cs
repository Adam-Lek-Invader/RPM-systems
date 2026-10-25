using UnityEngine;


public class RPM3_move : MonoBehaviour
{
    [Header("References")]
    public GameObject ObjOuterFrame;
    public GameObject ObjIntermediateFrame;
    public GameObject ObjInnerFrame;

    public button_press_stable StartButton;
    public input_field_grabber InputField_OuterSpeed;
    public input_field_grabber InputField_IntermediateSpeed;
    public input_field_grabber InputField_InnerSpeed;

    [Header("Public vars")]
    public float OuterSpeed = 0f;
    public float IntermediateSpeed = 0f;
    public float InnerSpeed = 0f;
    public bool isMoving = false;

    [Header("DC motor angles")]
    public float OuterAng = 0f;
    public float IntermediateAng = 0f;
    public float InnerAng = 0f;

    Vector3 speed_OuterFrame = Vector3.zero;
    Vector3 speed_IntermediateFrame = Vector3.zero;
    Vector3 speed_InnerFrame = Vector3.zero;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        isMoving = StartButton.isPressed;

        if (isMoving)
        {
            //speeds normalized from RPM to Deg
            OuterSpeed = InputField_OuterSpeed.input_float_val*6;
            IntermediateSpeed = InputField_IntermediateSpeed.input_float_val*6;
            InnerSpeed = InputField_InnerSpeed.input_float_val*6;

            speed_OuterFrame.z = OuterSpeed * Time.deltaTime;
            speed_IntermediateFrame.y = IntermediateSpeed * Time.deltaTime;
            speed_InnerFrame.x = InnerSpeed * Time.deltaTime;

            ObjOuterFrame.transform.Rotate(speed_OuterFrame, Space.Self);
            ObjIntermediateFrame.transform.Rotate(speed_IntermediateFrame, Space.Self);
            ObjInnerFrame.transform.Rotate(speed_InnerFrame, Space.Self);

            //calc dc angles
            OuterAng += OuterSpeed * Time.deltaTime;
            IntermediateAng += IntermediateSpeed * Time.deltaTime;
            InnerAng += InnerSpeed * Time.deltaTime;
            //normalize to <0, 360)
            if(OuterAng >= 360f) OuterAng -= 360f;
            if(IntermediateAng >= 360f) IntermediateAng -= 360f;
            if(InnerAng >= 360f) InnerAng -= 360f;
            if(OuterAng < 0f) OuterAng += 360f;
            if(IntermediateAng < 0f) IntermediateAng += 360f;
            if(InnerAng < 0f) InnerAng += 360f;
        }
    }
}
