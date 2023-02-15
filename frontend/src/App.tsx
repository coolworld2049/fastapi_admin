import { Admin, CustomRoutes, Resource, ShowGuesser } from "react-admin";
import { Route } from "react-router";
import MyLayout from "./components/AdminLayout";
import Dashboard from "./pages/Dashboard/Dashboard";
import LoginPage from "./pages/Login";
import { ProfileEdit } from "./pages/Profile/ProfileEdit";
import { UserCreate, UserEdit, UserList } from "./pages/Menu/Users";
import authProvider from "./providers/authProvider";
import PersonIcon from "@mui/icons-material/Person";
import { dataProvider } from "./providers/dataProvider";
import Moment from "react-moment";

// Sets the moment instance to use.
Moment.globalMoment = require("moment");

// Set the locale for every react-moment instance to French.
Moment.globalLocale = "en";

// Set the output format for every react-moment instance.
Moment.globalFormat = "D MMM YYYY";

// Set the timezone for every instance.
Moment.globalTimezone = "Europe/Moscow";

// Set the output timezone for local for every instance.
Moment.globalLocal = true;

// Use a <span> tag for every react-moment instance.
Moment.globalElement = "span";

// Upper case all rendered dates.
Moment.globalFilter = (d: string) => {
  return d.toUpperCase();
};

const App = () => {
  return (
    <Admin
      dataProvider={dataProvider}
      authProvider={authProvider}
      loginPage={LoginPage}
      layout={MyLayout}
      dashboard={Dashboard}
    >
      <CustomRoutes>
        <Route path="/my-profile" element={<ProfileEdit />} />
      </CustomRoutes>

      <Resource
        options={{ label: "User" }}
        name="users"
        list={UserList}
        edit={UserEdit}
        create={UserCreate}
        show={ShowGuesser}
        icon={PersonIcon}
      />
    </Admin>
  );
};

export default App;
