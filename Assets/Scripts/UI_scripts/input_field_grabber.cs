using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class input_field_grabber : MonoBehaviour
{
    [Header("Input Field value grabber")]

    public float input_float_val= 0f;
    public void GrabInputFieldValue(string input)
    {
        // if string == "" or null, set input_float_val to 0
        if (string.IsNullOrEmpty(input))
        {
            input_float_val = 0f; // Set to 0 if the input is empty
            return;
        }

        // Get the value from the input field
        string inputValue = input;
       
        for(int i = 0; i < inputValue.Length; i++)
        {
            if (inputValue[i] == '.')
            {
                inputValue = inputValue.Substring(0, i) + ',' + inputValue.Substring(i + 1);
            }
        }
        float.TryParse(inputValue, out input_float_val);
    }
}
