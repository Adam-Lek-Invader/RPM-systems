using UnityEngine;

public class RotateOnButton : MonoBehaviour
{
    public GameObject rpm_input_field;
    public GameObject start_button;
    public float rotationSpeed = 1f; // Speed of rotation
    public bool isRotating = false; // Flag to control rotation

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        isRotating = start_button.GetComponent<button_press_stable>().isPressed;
        if (isRotating)
        {
            rotationSpeed = rpm_input_field.GetComponent<input_field_grabber>().input_float_val;
            GetComponent<Transform>().Rotate(0, 0, rotationSpeed);
        }
    }
}
