/* eslint-disable react/no-unescaped-entities */
import { Command } from "@/components/custom/Terminal";


export const commands: Array<Command> = [
    {
      command: "help",
      result: (
        <div>
          <p>Available commands:</p>
          <ul>
            <li>
              <b>help</b> - List of available commands
            </li>
            <li>
              <b>bio</b> - Display bio details about the user
            </li>
          </ul>
        </div>
      ),
    },
    {
      command: "displaylogs",
      result: (
        <div>
          <p>
            👋 Hello! I'm user-name, a passionate developer with a love for coding and technology.
          </p>
          <ul>
            <li>💻 Full-Stack Developer</li>
            <li>📚 Avid Learner</li>
            <li>🎨 Creative Problem Solver</li>
            <li>🌐 Open Source Contributor</li>
          </ul>
          <p>Let's build something amazing together!</p>
        </div>
      ),
    },
  ];