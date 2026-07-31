using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class button_press_stable : MonoBehaviour
{
    [Header("Button Press Stable")]
    public bool isPressed = false;

    public void OnButtonPress()
    {
        isPressed = !isPressed; // Toggle the state of isPressed
    }
}
