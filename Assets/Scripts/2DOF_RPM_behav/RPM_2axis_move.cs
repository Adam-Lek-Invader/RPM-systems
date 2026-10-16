using UnityEngine;


public class RPM_move : MonoBehaviour
{
    [Header("References")]
    public GameObject ObjRotFrame;
    public GameObject ObjBeeChamber;

    public button_press_stable StartButton;
    public input_field_grabber InputField_RotFrameSpeed;
    public input_field_grabber InputField_BeeChamberSpeed;

    [Header("Public vars")]
    public float RotFrameSpeed = 0f;
    public float BeeChamberSpeed = 0f;
    public bool isMoving = false;

    Vector3 speed_RotFrame = Vector3.zero;
    Vector3 speed_BeeChamber = Vector3.zero;
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
            RotFrameSpeed = InputField_RotFrameSpeed.input_float_val*6;
            BeeChamberSpeed = InputField_BeeChamberSpeed.input_float_val*6;

            speed_RotFrame.z = RotFrameSpeed * Time.deltaTime;
            speed_BeeChamber.y = BeeChamberSpeed * Time.deltaTime;

            ObjRotFrame.transform.Rotate(speed_RotFrame, Space.Self);
            ObjBeeChamber.transform.Rotate(speed_BeeChamber, Space.Self);
        }
    }
}
