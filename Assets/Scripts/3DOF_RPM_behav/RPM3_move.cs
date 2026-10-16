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
            //speeds normalized to RPM
            OuterSpeed = InputField_OuterSpeed.input_float_val*6;
            IntermediateSpeed = InputField_IntermediateSpeed.input_float_val*6;
            InnerSpeed = InputField_InnerSpeed.input_float_val*6;

            speed_OuterFrame.z = OuterSpeed * Time.deltaTime;
            speed_IntermediateFrame.y = IntermediateSpeed * Time.deltaTime;
            speed_InnerFrame.x = InnerSpeed * Time.deltaTime;

            ObjOuterFrame.transform.Rotate(speed_OuterFrame, Space.Self);
            ObjIntermediateFrame.transform.Rotate(speed_IntermediateFrame, Space.Self);
            ObjInnerFrame.transform.Rotate(speed_InnerFrame, Space.Self);
        }
    }
}
